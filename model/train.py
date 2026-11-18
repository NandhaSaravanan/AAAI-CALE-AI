"""Step 4: siamese UniXcoder, cosine similarity, BCE on (scale*cos + bias).
Condition A: no transformation augmentation (positives = same-problem pairs only).
Condition B: same pair budget; half of positives replaced by train-family transform pairs
             (rename, reorder). Negatives identical across A and B.
After training: embeds every val/test program and writes eval/scores/learned_{A,B}_{split}.jsonl."""
import argparse, json, math, os, random, time
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

EXP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load(path):
    return [json.loads(l) for l in open(path)]


def build_train(cond, n_pos, n_neg, seed):
    rng = random.Random(seed)
    P = load(os.path.join(EXP, "data", "pairs_train.jsonl"))
    sp = [p for p in P if p["pair_type"] == "same_problem"]
    tr = [p for p in P if p["pair_type"] == "transform"]
    hard = [p for p in P if p["pair_type"] == "hard_struct"]
    rnd = [p for p in P if p["pair_type"] == "random"]
    for L in (sp, tr, hard, rnd):
        L.sort(key=lambda p: (p["id_a"], p["id_b"]))
        rng.shuffle(L)
    neg = hard[: n_neg // 2] + rnd[: n_neg - n_neg // 2]
    if cond == "A":
        pos = sp[:n_pos]
    else:
        reo = [p for p in tr if p["family"] == "reorder"]
        ren = [p for p in tr if p["family"] == "rename"]
        k = n_pos // 2
        aug = (reo + ren)[:k]
        pos = sp[: n_pos - len(aug)] + aug
    data = pos + neg
    rng.shuffle(data)
    return data


class Enc(torch.nn.Module):
    def __init__(self, name, freeze):
        super().__init__()
        # attention-prob dropout disabled: MPS scaled_dot_product_attention does not support dropout
        self.m = AutoModel.from_pretrained(name, attention_probs_dropout_prob=0.0)
        for n, p in self.m.named_parameters():
            if n.startswith("embeddings") or any(n.startswith(f"encoder.layer.{i}.") for i in range(freeze)):
                p.requires_grad = False
        self.scale = torch.nn.Parameter(torch.tensor(10.0))
        self.bias = torch.nn.Parameter(torch.tensor(-5.0))

    def embed(self, ids, mask):
        h = self.m(input_ids=ids, attention_mask=mask).last_hidden_state
        e = (h * mask.unsqueeze(-1)).sum(1) / mask.sum(1, keepdim=True)
        return F.normalize(e.float(), dim=-1)


def batches(data, bs, rng, lens):
    idx = list(range(len(data)))
    rng.shuffle(idx)
    out = []
    for i in range(0, len(idx), bs * 50):  # length-bucketing inside mega-batches
        chunk = sorted(idx[i:i + bs * 50], key=lambda j: lens[j])
        out += [chunk[k:k + bs] for k in range(0, len(chunk), bs)]
    rng.shuffle(out)
    return out


@torch.no_grad()
def embed_all(model, tok, ids, src, dev, cfg):
    model.eval()
    order = sorted(ids, key=lambda i: len(src[i]))
    E = {}
    for k in range(0, len(order), 64):
        b = order[k:k + 64]
        x = tok([src[i] for i in b], padding=True, truncation=True, max_length=cfg["max_len"], return_tensors="pt").to(dev)
        with torch.autocast("mps", dtype=torch.bfloat16, enabled=cfg["bf16"]):
            e = model.embed(x["input_ids"], x["attention_mask"])
        for i, v in zip(b, e.cpu().numpy()):
            E[i] = v
    model.train()
    return E


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", choices=["A", "B"], required=True)
    a = ap.parse_args()
    cfg = dict(model="microsoft/unixcoder-base", cond=a.cond, seed=42, epochs=3, batch_pairs=16, lr=2e-5,
               weight_decay=0.01, warmup_frac=0.06, max_len=256, freeze_layers=6, bf16=True, n_pos=4000, n_neg=4000,
               device="mps", note="Lower 6/12 layers + embeddings frozen and 3 epochs due to Apple M4 (MPS) compute budget; "
                                  "identical for A and B. Attention-prob dropout=0 (MPS SDPA limitation). Last-epoch checkpoint used (no checkpoint selection).")
    os.makedirs(os.path.join(EXP, "configs"), exist_ok=True)
    json.dump(cfg, open(os.path.join(EXP, "configs", f"train_{a.cond}.json"), "w"), indent=1)
    random.seed(cfg["seed"]); np.random.seed(cfg["seed"]); torch.manual_seed(cfg["seed"])
    dev = torch.device(cfg["device"])
    progs = {p["id"]: p for p in load(os.path.join(EXP, "data", "programs.jsonl"))}
    src = {k: v["src"] for k, v in progs.items()}
    data = build_train(a.cond, cfg["n_pos"], cfg["n_neg"], cfg["seed"])
    with open(os.path.join(EXP, "configs", f"train_pairs_{a.cond}.jsonl"), "w") as f:
        for p in data:
            f.write(json.dumps({k: p[k] for k in ("id_a", "id_b", "label", "family", "pair_type")}) + "\n")
    tok = AutoTokenizer.from_pretrained(cfg["model"])
    tl = {i: min(cfg["max_len"], len(s) // 3) for i, s in src.items()}
    lens = [max(tl[p["id_a"]], tl[p["id_b"]]) for p in data]
    model = Enc(cfg["model"], cfg["freeze_layers"]).to(dev)
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=cfg["lr"], weight_decay=cfg["weight_decay"])
    rng = random.Random(cfg["seed"])
    steps_per_epoch = math.ceil(len(data) / cfg["batch_pairs"])
    total = steps_per_epoch * cfg["epochs"]
    warm = int(total * cfg["warmup_frac"])
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1, (s + 1) / max(1, warm)) * max(0.0, (total - s) / max(1, total - warm)))
    logp = os.path.join(EXP, "model", f"train_log_{a.cond}.jsonl")
    logf = open(logp, "w")
    step, t0 = 0, time.time()
    model.train()
    for ep in range(cfg["epochs"]):
        for b in batches(data, cfg["batch_pairs"], rng, lens):
            pa = [data[j] for j in b]
            texts = [src[p["id_a"]] for p in pa] + [src[p["id_b"]] for p in pa]
            x = tok(texts, padding=True, truncation=True, max_length=cfg["max_len"], return_tensors="pt").to(dev)
            y = torch.tensor([p["label"] for p in pa], dtype=torch.float32, device=dev)
            with torch.autocast("mps", dtype=torch.bfloat16, enabled=cfg["bf16"]):
                e = model.embed(x["input_ids"], x["attention_mask"])
            n = len(pa)
            cos = (e[:n] * e[n:]).sum(-1)
            loss = F.binary_cross_entropy_with_logits(model.scale * cos + model.bias, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step(); sched.step(); opt.zero_grad()
            step += 1
            if step % 25 == 0:
                rec = {"step": step, "epoch": ep, "loss": round(loss.item(), 4), "lr": sched.get_last_lr()[0],
                       "elapsed_s": round(time.time() - t0, 1), "total_steps": total}
                logf.write(json.dumps(rec) + "\n"); logf.flush()
                print(rec, flush=True)
    ck = os.path.join(EXP, "model", "checkpoints", a.cond)
    os.makedirs(ck, exist_ok=True)
    torch.save({k: v for k, v in model.state_dict().items()}, os.path.join(ck, "model.pt"))
    # score val + test pairs
    os.makedirs(os.path.join(EXP, "eval", "scores"), exist_ok=True)
    for split in ["val", "test"]:
        pairs = load(os.path.join(EXP, "data", f"pairs_{split}.jsonl"))
        ids = sorted({p["id_a"] for p in pairs} | {p["id_b"] for p in pairs})
        E = embed_all(model, tok, ids, src, dev, cfg)
        with open(os.path.join(EXP, "eval", "scores", f"learned_{a.cond}_{split}.jsonl"), "w") as f:
            for p in pairs:
                f.write(json.dumps({"id_a": p["id_a"], "id_b": p["id_b"], "score": float(np.dot(E[p["id_a"]], E[p["id_b"]]))}) + "\n")
    logf.write(json.dumps({"done": True, "elapsed_s": round(time.time() - t0, 1)}) + "\n")
    print("done", time.time() - t0)


if __name__ == "__main__":
    main()
