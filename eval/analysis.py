"""Post-hoc analysis of the main run (seed 42), JPlag-scorable view, from existing score files only
(no new models, detectors or transformation families). Thresholds: 1% FPR on validation negatives,
exactly as in evaluate.py.
  1. Held-out (dead-code) TPR@1% per detector, split by relative insertion size
     (variant tokens / original tokens - 1, Python tokenize, comments/whitespace excluded), terciles.
  2. Held-out TPR@1% split by original program length (tokens), terciles.
  3. Realized test FPR at the 1% threshold, separately on hard (structurally similar) and random negatives.
  4. Overlap of missed dead-code pairs between detectors (B vs Dolos, B vs JPlag).
Writes eval/analysis.csv (long format) and eval/analysis.md."""
import csv, io, json, os, tokenize
import numpy as np

from evaluate import E, EXP, load_pairs, load_scores, scorable, thr_at

DETS = ["learned_0", "learned_A", "learned_B", "jplag", "moss", "dolos"]
SKIP = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER}


def ntok(src):
    try:
        return sum(1 for t in tokenize.generate_tokens(io.StringIO(src).readline) if t.type not in SKIP)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return None


def tercile_bins(x):
    q = np.quantile(x, [1 / 3, 2 / 3])
    return np.digitize(x, q, right=True), q  # 0,1,2


def main():
    progs = {p["id"]: p for p in map(json.loads, open(os.path.join(EXP, "data", "programs.jsonl")))}
    sv_, st_ = scorable("val"), scorable("test")
    val = [p for p in load_pairs("val") if (p["id_a"], p["id_b"]) in sv_]
    test = [p for p in load_pairs("test") if (p["id_a"], p["id_b"]) in st_]
    held = [p for p in test if p["label"] == 1 and p["family"] == "deadcode"]
    neg = [p for p in test if p["label"] == 0]
    flag, negflag = {}, {}
    for d in DETS:
        sv, stt = load_scores(d, "val"), load_scores(d, "test")
        t = thr_at(np.array([sv[(p["id_a"], p["id_b"])] for p in val if p["label"] == 0]), 0.01)
        flag[d] = np.array([stt[(p["id_a"], p["id_b"])] > t for p in held])
        negflag[d] = np.array([stt[(p["id_a"], p["id_b"])] > t for p in neg])
    # original = the non-variant side of each dead-code pair
    orig = [p["id_a"] if "#" not in p["id_a"] else p["id_b"] for p in held]
    var = [p["id_b"] if "#" not in p["id_a"] else p["id_a"] for p in held]
    to = np.array([ntok(progs[i]["src"]) for i in orig], dtype=float)
    tv = np.array([ntok(progs[i]["src"]) for i in var], dtype=float)
    ok = ~(np.isnan(to) | np.isnan(tv))
    rows = []
    for kind, x in (("insertion", tv / to - 1), ("length", to)):
        b, q = tercile_bins(x[ok])
        for k in range(3):
            m = b == k
            lo = x[ok][m].min(); hi = x[ok][m].max()
            for d in DETS:
                rows.append({"analysis": kind, "bin": k, "lo": lo, "hi": hi, "n": int(m.sum()), "detector": d,
                             "value": float(flag[d][ok][m].mean())})
    hard = np.array([p["pair_type"] == "hard_struct" for p in neg])
    for typ, m in (("hard_struct", hard), ("random", ~hard)):
        for d in DETS:
            rows.append({"analysis": "neg_fpr", "bin": typ, "lo": "", "hi": "", "n": int(m.sum()), "detector": d,
                         "value": float(negflag[d][m].mean())})
    for a, b in (("learned_B", "dolos"), ("learned_B", "jplag"), ("learned_B", "moss")):
        ma, mb = ~flag[a], ~flag[b]
        for k, v in (("missed_a", ma.sum()), ("missed_b", mb.sum()), ("missed_both", (ma & mb).sum()),
                     ("missed_a_caught_b", (ma & ~mb).sum()), ("missed_b_caught_a", (mb & ~ma).sum()),
                     ("caught_either", (~ma | ~mb).sum())):
            rows.append({"analysis": f"overlap:{a}:{b}", "bin": k, "lo": "", "hi": "", "n": len(held), "detector": "", "value": int(v)})
    rows.append({"analysis": "meta", "bin": "n_held_tokenized", "lo": "", "hi": "", "n": int(ok.sum()), "detector": "", "value": int(len(held))})
    with open(os.path.join(E, "analysis.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})
    with open(os.path.join(E, "analysis.md"), "w") as f:
        f.write("# Post-hoc analysis (main run, seed 42, JPlag-scorable view; 1%-FPR validation thresholds)\n\n")
        for kind in ("insertion", "length"):
            f.write(f"## Held-out TPR@1% by {kind} tercile\n\n| bin | range | n | " + " | ".join(DETS) + " |\n|---|---|---|" + "---|" * len(DETS) + "\n")
            for k in range(3):
                R = [r for r in rows if r["analysis"] == kind and r["bin"] == k]
                f.write(f"| {k} | {R[0]['lo']:.3f}–{R[0]['hi']:.3f} | {R[0]['n']} | " + " | ".join(f"{100 * r['value']:.1f}" for r in R) + " |\n")
            f.write("\n")
        f.write("## Realized test FPR (%) at the 1% threshold by negative type\n\n| type | n | " + " | ".join(DETS) + " |\n|---|---|" + "---|" * len(DETS) + "\n")
        for typ in ("hard_struct", "random"):
            R = [r for r in rows if r["analysis"] == "neg_fpr" and r["bin"] == typ]
            f.write(f"| {typ} | {R[0]['n']} | " + " | ".join(f"{100 * r['value']:.1f}" for r in R) + " |\n")
        f.write("\n## Missed dead-code pairs (overlap)\n\n")
        for r in rows:
            if r["analysis"].startswith("overlap"):
                f.write(f"- {r['analysis']} {r['bin']}: {r['value']} of {r['n']}\n")
    print(open(os.path.join(E, "analysis.md")).read())


if __name__ == "__main__":
    main()
