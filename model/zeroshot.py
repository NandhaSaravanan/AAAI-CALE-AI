"""Reference point: pretrained UniXcoder with NO fine-tuning (mean-pooled, cosine).
Writes eval/scores/learned_0_{val,test}.jsonl."""
import json, os, sys
import numpy as np
import torch
from transformers import AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
from train import EXP, Enc, embed_all, load  # noqa: E402

cfg = {"model": "microsoft/unixcoder-base", "max_len": 256, "bf16": True}
json.dump(dict(cfg, note="zero-shot, no training"), open(os.path.join(EXP, "configs", "zeroshot.json"), "w"), indent=1)
dev = torch.device("mps")
src = {p["id"]: p["src"] for p in load(os.path.join(EXP, "data", "programs.jsonl"))}
tok = AutoTokenizer.from_pretrained(cfg["model"])
model = Enc(cfg["model"], 0).to(dev)
for split in ["val", "test"]:
    pairs = load(os.path.join(EXP, "data", f"pairs_{split}.jsonl"))
    ids = sorted({p["id_a"] for p in pairs} | {p["id_b"] for p in pairs})
    E = embed_all(model, tok, ids, src, dev, cfg)
    with open(os.path.join(EXP, "eval", "scores", f"learned_0_{split}.jsonl"), "w") as f:
        for p in pairs:
            f.write(json.dumps({"id_a": p["id_a"], "id_b": p["id_b"], "score": float(np.dot(E[p["id_a"]], E[p["id_b"]]))}) + "\n")
print("done")
