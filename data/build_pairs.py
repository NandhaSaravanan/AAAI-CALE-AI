"""Step 3: splits and pairs.
* Split unit = problem ID (stricter than original program: all variants of an original, and all
  originals of a problem, land in one split).  70/10/20 train/val/test by problem.
* Families: train = {rename, reorder}; held-out = {deadcode} (appears ONLY in test).
* Positive pair types:  transform (original vs verified variant; family = rename/reorder/deadcode),
                        same_problem (two different accepted solutions of the same problem).
* Negative pair types:  hard_struct (different problems, highest token-structure 4-gram Jaccard),
                        random (different problems).
  Not built: "same problem, semantically different" negatives — Python800 contains only Accepted
  solutions, so no such programs exist in the dataset.
Outputs data/pairs_{split}.jsonl, data/programs.jsonl (id -> src), data/split_report.md."""
import io, json, os, random, tokenize, keyword, warnings
from collections import defaultdict
warnings.filterwarnings("ignore")

EXP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRAIN_FAMS, HELDOUT = ["rename", "reorder"], ["deadcode"]
N_HARD, N_RAND = 4, 6
SEED = 7


def struct_ngrams(src, n=4):
    toks = []
    try:
        for t in tokenize.generate_tokens(io.StringIO(src).readline):
            if t.type == tokenize.NAME:
                toks.append(t.string if keyword.iskeyword(t.string) else "ID")
            elif t.type == tokenize.OP:
                toks.append(t.string)
            elif t.type in (tokenize.NUMBER, tokenize.STRING):
                toks.append("LIT")
    except Exception:
        pass
    return {tuple(toks[i:i + n]) for i in range(max(0, len(toks) - n + 1))}


def jacc(a, b):
    return len(a & b) / max(1, len(a | b))


def main():
    rng = random.Random(SEED)
    P = [json.loads(l) for l in open(os.path.join(EXP, "work", "programs.jsonl"))]
    pids = sorted({p["pid"] for p in P})
    rng.shuffle(pids)
    n = len(pids)
    split_of = {}
    for i, pid in enumerate(pids):
        split_of[pid] = "train" if i < 0.7 * n else ("val" if i < 0.8 * n else "test")
    origs = defaultdict(list)          # split -> originals
    variants = defaultdict(list)       # group -> variants
    for p in P:
        if p["family"] == "original":
            origs[split_of[p["pid"]]].append(p)
        else:
            variants[p["source_group"]].append(p)
    with open(os.path.join(EXP, "data", "programs.jsonl"), "w") as f:
        for p in P:
            f.write(json.dumps({"id": p["id"], "pid": p["pid"], "family": p["family"], "source_group": p["source_group"],
                                "split": split_of[p["pid"]], "src": p["src"]}) + "\n")
    counts = {}
    for split in ["train", "val", "test"]:
        O = origs[split]
        fams_allowed = TRAIN_FAMS + (HELDOUT if split == "test" else [])
        pairs = []
        for o in O:
            for v in variants[o["id"]]:
                if v["family"] in fams_allowed:
                    pairs.append({"id_a": o["id"], "id_b": v["id"], "label": 1, "family": v["family"],
                                  "pair_type": "transform", "source_group": o["id"], "source_group_b": o["id"]})
        byp = defaultdict(list)
        for o in O:
            byp[o["pid"]].append(o)
        for pid, L in byp.items():
            for i in range(len(L)):
                for j in range(i + 1, len(L)):
                    pairs.append({"id_a": L[i]["id"], "id_b": L[j]["id"], "label": 1, "family": "same_problem",
                                  "pair_type": "same_problem", "source_group": L[i]["id"], "source_group_b": L[j]["id"]})
        grams = {o["id"]: struct_ngrams(o["src"]) for o in O}
        seen = set()
        for o in O:
            others = [x for x in O if x["pid"] != o["pid"]]
            sims = sorted(others, key=lambda x: -jacc(grams[o["id"]], grams[x["id"]]))
            hard = [x for x in sims[: N_HARD * 3] if (o["id"], x["id"]) not in seen][:N_HARD]
            rand = rng.sample(others, N_RAND)
            for x, t in [(h, "hard_struct") for h in hard] + [(r, "random") for r in rand]:
                key = tuple(sorted((o["id"], x["id"])))
                if key in seen:
                    continue
                seen.add(key)
                pairs.append({"id_a": o["id"], "id_b": x["id"], "label": 0, "family": "negative",
                              "pair_type": t, "source_group": o["id"], "source_group_b": x["id"]})
        rng.shuffle(pairs)
        with open(os.path.join(EXP, "data", f"pairs_{split}.jsonl"), "w") as f:
            for p in pairs:
                f.write(json.dumps(p) + "\n")
        c = defaultdict(int)
        for p in pairs:
            c[(p["label"], p["family"], p["pair_type"])] += 1
        counts[split] = (len({o["pid"] for o in O}), len(O), dict(c), len(pairs))
    with open(os.path.join(EXP, "data", "split_report.md"), "w") as f:
        f.write("# Splits and pairs (Step 3)\n\n")
        f.write(f"Split unit: problem ID (70/10/20 by problem, seed {SEED}); every original and all of its variants are in one split.\n\n")
        f.write(f"Train families: {TRAIN_FAMS}. Held-out family: {HELDOUT} (test split only; never in train/val).\n\n")
        f.write("Negatives per original: up to %d hard_struct (top token-structure 4-gram Jaccard, different problem) + %d random different-problem.\n\n" % (N_HARD, N_RAND))
        f.write("Not built: same-problem semantically-different negatives (Python800 has only Accepted solutions).\n\n")
        f.write("| split | problems | originals | label | family | pair_type | count |\n|---|---|---|---|---|---|---|\n")
        for s, (np_, no, c, tot) in counts.items():
            for (lab, fam, pt), k in sorted(c.items()):
                f.write(f"| {s} | {np_} | {no} | {lab} | {fam} | {pt} | {k} |\n")
            f.write(f"| {s} | | | | **total** | | **{tot}** |\n")
    print(open(os.path.join(EXP, "data", "split_report.md")).read())


if __name__ == "__main__":
    main()
