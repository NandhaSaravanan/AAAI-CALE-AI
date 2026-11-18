"""Seed robustness: per training seed (42 = main run, 1, 2), TPR@1%/5% FPR and AUC for A and B on
seen / held-out subsets (same protocol and JPlag-scorable view as evaluate.py), the B-A difference per
seed, and mean +/- sample s.d. across seeds. Writes eval/seeds.csv and eval/seeds.md."""
import csv, json, os, statistics as st
import numpy as np
from sklearn.metrics import roc_auc_score

from evaluate import EXP, E, FPRS, load_pairs, load_scores, scorable, thr_at

SEEDS = [42, 1, 2]
SUBS = {"seen": {"rename", "reorder"}, "heldout": {"deadcode"}}


def det(cond, seed):
    return f"learned_{cond}" if seed == 42 else f"learned_{cond}_s{seed}"


def metrics(name, val, test):
    sv, stt = load_scores(name, "val"), load_scores(name, "test")
    if sv is None or stt is None:
        return None
    vneg = np.array([sv[(p["id_a"], p["id_b"])] for p in val if p["label"] == 0])
    thr = {f: thr_at(vneg, f) for f in FPRS}
    neg = [p for p in test if p["label"] == 0]
    out = {}
    for sub, fams in SUBS.items():
        P = [p for p in test if p["label"] == 1 and p["family"] in fams] + neg
        y = np.array([p["label"] for p in P]); s = np.array([stt[(p["id_a"], p["id_b"])] for p in P])
        out[(sub, "auc")] = roc_auc_score(y, s)
        for f in FPRS:
            out[(sub, f"tpr@{int(f * 100)}")] = float((s[y == 1] > thr[f]).mean())
    return out


def main():
    sv_, st_ = scorable("val"), scorable("test")
    val = [p for p in load_pairs("val") if (p["id_a"], p["id_b"]) in sv_]
    test = [p for p in load_pairs("test") if (p["id_a"], p["id_b"]) in st_]
    rows, per = [], {}
    for seed in SEEDS:
        ma, mb = metrics(det("A", seed), val, test), metrics(det("B", seed), val, test)
        if ma is None or mb is None:
            continue
        per[seed] = (ma, mb)
        for (sub, m) in ma:
            rows.append({"seed": seed, "subset": sub, "metric": m, "A": ma[(sub, m)], "B": mb[(sub, m)], "B_minus_A": mb[(sub, m)] - ma[(sub, m)]})
    with open(os.path.join(E, "seeds.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})
    with open(os.path.join(E, "seeds.md"), "w") as f:
        f.write(f"# Seed robustness (JPlag-scorable view), seeds = {sorted(per)}\n\nTPR in %, AUC raw. mean ± s.d. over seeds; per-seed values in seeds.csv.\n\n")
        f.write("| subset | metric | A | B | B − A | B − A per seed |\n|---|---|---|---|---|---|\n")
        for sub in SUBS:
            for m in ["tpr@1", "tpr@5", "auc"]:
                k = 1 if m == "auc" else 100
                a = [per[s][0][(sub, m)] * k for s in per]; b = [per[s][1][(sub, m)] * k for s in per]
                d = [y - x for x, y in zip(a, b)]
                fmt = (lambda v: f"{v:.3f}") if m == "auc" else (lambda v: f"{v:.1f}")
                sd = (lambda L: st.stdev(L) if len(L) > 1 else float("nan"))
                f.write(f"| {sub} | {m} | {fmt(st.mean(a))} ± {fmt(sd(a))} | {fmt(st.mean(b))} ± {fmt(sd(b))} | "
                        f"{fmt(st.mean(d))} ± {fmt(sd(d))} | {', '.join(fmt(x) for x in d)} |\n")
    print(open(os.path.join(E, "seeds.md")).read())


if __name__ == "__main__":
    main()
