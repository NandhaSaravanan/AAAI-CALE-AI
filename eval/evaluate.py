"""Step 6: evaluation at matched FPR with group bootstrap.
Thresholds: per detector, chosen on VAL negatives so that val FPR <= 1% (and 5%); a pair is
flagged if score > threshold. TPR is then measured on TEST subsets:
  seen      = test transform positives of families {rename, reorder}   + all test negatives
  heldout   = test transform positives of family  {deadcode}           + all test negatives
  rename / reorder / deadcode individually, and same_problem (+ all negatives) for reference.
AUC is threshold-free on each subset. 95% CIs: 1000-rep bootstrap over source_group (original
program; negatives belong to the group of id_a), thresholds held fixed.
Writes results.csv, deltas.csv, roc_seen.png, roc_heldout.png, summary.md (in eval/)."""
import csv, json, os
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EXP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
E = os.path.join(EXP, "eval")
DET = [("learned_0", "UniXcoder zero-shot"), ("learned_A", "UniXcoder-A (no aug.)"), ("learned_B", "UniXcoder-B (aug.)"), ("jplag", "JPlag 6.3"), ("dolos", "Dolos 2.10")]
COL = {"learned_0": "#6250d6", "learned_A": "#2a78d6", "learned_B": "#eb6834", "jplag": "#1baf7a", "dolos": "#eda100"}  # validated slots 1-4
LS = {"learned_0": "-.", "learned_A": "-", "learned_B": "-", "jplag": "--", "dolos": ":"}
SUBSETS = {"seen": {"rename", "reorder"}, "heldout": {"deadcode"}, "rename": {"rename"}, "reorder": {"reorder"},
           "deadcode": {"deadcode"}, "same_problem": {"same_problem"}}
FPRS = [0.01, 0.05]
B = 1000


def load_pairs(split):
    return [json.loads(l) for l in open(os.path.join(EXP, "data", f"pairs_{split}.jsonl"))]


def load_scores(det, split):
    p = os.path.join(E, "scores", f"{det}_{split}.jsonl")
    if not os.path.exists(p):
        return None
    return {(r["id_a"], r["id_b"]): r["score"] for r in map(json.loads, open(p))}


def thr_at(neg, fpr):
    s = np.sort(neg)[::-1]
    k = int(np.floor(fpr * len(s)))
    return s[k]  # flag if score > s[k]  =>  at most k negatives flagged


def scorable(split):
    """Pairs where JPlag accepted both submissions (>= its default 12-token minimum)."""
    return {(r["id_a"], r["id_b"]) for r in map(json.loads, open(os.path.join(E, "scores", f"jplag_{split}.jsonl"))) if r["scored"]}


def main():
    import sys
    view = sys.argv[1] if len(sys.argv) > 1 else "scorable"
    val, test = load_pairs("val"), load_pairs("test")
    if view == "scorable":
        sv_, st_ = scorable("val"), scorable("test")
        val = [p for p in val if (p["id_a"], p["id_b"]) in sv_]
        test = [p for p in test if (p["id_a"], p["id_b"]) in st_]
    else:
        os.makedirs(os.path.join(E, "view_all"), exist_ok=True)
    OUT = E if view == "scorable" else os.path.join(E, "view_all")
    groups = sorted({p["source_group"] for p in test})
    gi = {g: i for i, g in enumerate(groups)}
    rng = np.random.default_rng(0)
    W = rng.multinomial(len(groups), np.ones(len(groups)) / len(groups), size=B)  # B x G group counts
    rows, curves, avail, boot_store = [], {}, [], {}
    for det, name in DET:
        sv, st = load_scores(det, "val"), load_scores(det, "test")
        if sv is None or st is None:
            continue
        avail.append(det)
        vneg = np.array([sv[(p["id_a"], p["id_b"])] for p in val if p["label"] == 0])
        thr = {f: thr_at(vneg, f) for f in FPRS}
        neg = [p for p in test if p["label"] == 0]
        for sub, fams in SUBSETS.items():
            pos = [p for p in test if p["label"] == 1 and p["family"] in fams]
            P = pos + neg
            y = np.array([p["label"] for p in P])
            s = np.array([st[(p["id_a"], p["id_b"])] for p in P])
            g = np.array([gi[p["source_group"]] for p in P])
            w = W[:, g]  # B x n weights
            auc = roc_auc_score(y, s)
            bauc = np.array([roc_auc_score(y, s, sample_weight=w[b]) for b in range(B)])
            rec = {"detector": det, "subset": sub, "n_pos": int(y.sum()), "n_neg": int((1 - y).sum()),
                   "auc": auc, "auc_lo": np.percentile(bauc, 2.5), "auc_hi": np.percentile(bauc, 97.5)}
            boot_store[(det, sub, "auc")] = bauc
            for f in FPRS:
                flag = (s > thr[f]).astype(float)
                tpr = flag[y == 1].mean()
                fpr = flag[y == 0].mean()
                bt = (w[:, y == 1] * flag[y == 1]).sum(1) / np.maximum(1, w[:, y == 1].sum(1))
                tag = f"{int(f * 100)}"
                rec.update({f"thr@{tag}": thr[f], f"tpr@{tag}": tpr, f"tpr@{tag}_lo": np.percentile(bt, 2.5),
                            f"tpr@{tag}_hi": np.percentile(bt, 97.5), f"test_fpr@{tag}": fpr})
                boot_store[(det, sub, f"tpr@{tag}")] = bt
            rows.append(rec)
            if sub in ("seen", "heldout"):
                fp, tp, _ = roc_curve(y, s)
                curves[(det, sub)] = (fp, tp, auc)
    keys = list(rows[0].keys())
    with open(os.path.join(OUT, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})
    # paired deltas (same bootstrap resamples)
    comps = [("learned_B", "learned_A")] + [(l, b) for l in ("learned_A", "learned_B") for b in ("jplag", "dolos") if b in avail]
    drows = []
    for a, b in comps:
        if a not in avail or b not in avail:
            continue
        ra = {r["subset"]: r for r in rows if r["detector"] == a}
        rb = {r["subset"]: r for r in rows if r["detector"] == b}
        for sub in ("seen", "heldout"):
            for m in ("auc", "tpr@1", "tpr@5"):
                d = boot_store[(a, sub, m)] - boot_store[(b, sub, m)]
                drows.append({"a": a, "b": b, "subset": sub, "metric": m, "delta": ra[sub][m] - rb[sub][m],
                              "lo": np.percentile(d, 2.5), "hi": np.percentile(d, 97.5),
                              "frac_boot_le_0": float((d <= 0).mean())})
    with open(os.path.join(OUT, "deltas.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, list(drows[0].keys()))
        w.writeheader()
        for r in drows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})
    # ROC figures (log-x to show the low-FPR region that matters)
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b",
                         "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.6), sharey=True)
    for ax, sub, title in [(axes[0], "seen", "Seen families (rename, reorder)"), (axes[1], "heldout", "Held-out family (dead code)")]:
        for det, name in DET:
            if (det, sub) not in curves:
                continue
            fp, tp, auc = curves[(det, sub)]
            ax.plot(np.maximum(fp, 1e-4), tp, LS[det], color=COL[det], lw=2, label=f"{name}  AUC {auc:.3f}")
        for f in FPRS:
            ax.axvline(f, color="#c3c2b7", lw=0.8, zorder=0)
        ax.set_xscale("log"); ax.set_xlim(1e-3, 1); ax.set_ylim(0, 1.01)
        ax.set_xlabel("False-positive rate (log)"); ax.set_title(title, fontsize=8.5, loc="left")
        ax.grid(axis="y", color="#e6e5e0", lw=0.6)
        ax.legend(frameon=False, fontsize=6.5, loc="lower right")
    axes[0].set_ylabel("True-positive rate")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "roc_main.png"), dpi=200)
    fig.savefig(os.path.join(OUT, "roc_main.pdf"))
    for sub in ("seen", "heldout"):
        f2, ax = plt.subplots(figsize=(3.3, 2.6))
        for det, name in DET:
            if (det, sub) in curves:
                fp, tp, auc = curves[(det, sub)]
                ax.plot(np.maximum(fp, 1e-4), tp, LS[det], color=COL[det], lw=2, label=f"{name} ({auc:.3f})")
        ax.set_xscale("log"); ax.set_xlim(1e-3, 1); ax.set_xlabel("FPR (log)"); ax.set_ylabel("TPR")
        ax.legend(frameon=False, fontsize=6); f2.tight_layout(); f2.savefig(os.path.join(OUT, f"roc_{sub}.png"), dpi=200)
    # summary
    with open(os.path.join(OUT, "summary.md"), "w") as f:
        f.write(f"# Evaluation summary (Step 6) — view: {view}\n\nView 'scorable' = only pairs where JPlag accepted both files (>=12 tokens), applied to ALL detectors; view 'all' = every pair, JPlag-unscorable pairs scored 0.\n\nDetectors evaluated: " + ", ".join(avail) + ". Moss: skipped (no user ID).\n\n")
        f.write("Thresholds set on val negatives (FPR<=1% / 5%); TPR on test. 95% CI = 1000x bootstrap over source_group.\n\n")
        f.write("| detector | subset | n_pos | n_neg | AUC [95% CI] | TPR@1%FPR [CI] | test FPR@1 | TPR@5%FPR [CI] | test FPR@5 |\n|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['detector']} | {r['subset']} | {r['n_pos']} | {r['n_neg']} | {r['auc']:.3f} [{r['auc_lo']:.3f}, {r['auc_hi']:.3f}] | "
                    f"{r['tpr@1']:.3f} [{r['tpr@1_lo']:.3f}, {r['tpr@1_hi']:.3f}] | {r['test_fpr@1']:.3f} | "
                    f"{r['tpr@5']:.3f} [{r['tpr@5_lo']:.3f}, {r['tpr@5_hi']:.3f}] | {r['test_fpr@5']:.3f} |\n")
        f.write("\n## Paired differences (a - b), bootstrap 95% CI\n\n| a | b | subset | metric | delta | CI |\n|---|---|---|---|---|---|\n")
        for r in drows:
            f.write(f"| {r['a']} | {r['b']} | {r['subset']} | {r['metric']} | {r['delta']:+.3f} | [{r['lo']:+.3f}, {r['hi']:+.3f}] |\n")
    print(open(os.path.join(OUT, "summary.md")).read())


if __name__ == "__main__":
    main()
