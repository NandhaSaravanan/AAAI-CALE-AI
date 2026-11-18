"""Final-pass Step 4: seed-averaged TPR@1%FPR with 95% bootstrap CIs resampled over PROBLEM IDs.
For each training seed (42 = the main run, called "seed-0" in the plan; 1; 2) and condition (A, B):
threshold at 1% FPR on that run's validation negatives (JPlag-scorable view, as everywhere);
per test positive pair a 0/1 flag. Bootstrap: resample test problem IDs with replacement (1,000 reps,
same resamples for all seeds/conditions); per rep, TPR per seed (weighted by problem multiplicity),
then averaged over seeds. Reports mean over seeds, CI, and the B-A seed-averaged difference.
The paper's seed-paragraph conclusion uses the fixed sign rule in paper/make_numbers.py (unchanged),
re-stated here. Writes eval/seed_summary.md and eval/seed_summary.csv."""
import csv, json, os
import numpy as np

from evaluate import EXP, E, load_pairs, load_scores, scorable, thr_at

SEEDS = [42, 1, 2]
FAMS = {"rename": {"rename"}, "reorder": {"reorder"}, "deadcode (held-out)": {"deadcode"},
        "seen pooled": {"rename", "reorder"}, "same_problem": {"same_problem"}}
B = 1000


def name(c, s):
    return f"learned_{c}" if s == 42 else f"learned_{c}_s{s}"


def main():
    sv_, st_ = scorable("val"), scorable("test")
    val = [p for p in load_pairs("val") if (p["id_a"], p["id_b"]) in sv_]
    test = [p for p in load_pairs("test") if (p["id_a"], p["id_b"]) in st_]
    pos = [p for p in test if p["label"] == 1]
    pid = lambda i: i.split("/")[0]
    pids = sorted({pid(p["id_a"]) for p in test})
    pi = {x: k for k, x in enumerate(pids)}
    g = np.array([pi[pid(p["id_a"])] for p in pos])
    rng = np.random.default_rng(0)
    W = rng.multinomial(len(pids), np.ones(len(pids)) / len(pids), size=B)[:, g]  # B x n_pos
    flags = {}
    for c in "AB":
        for s in SEEDS:
            sv, stt = load_scores(name(c, s), "val"), load_scores(name(c, s), "test")
            if sv is None or stt is None:
                raise SystemExit(f"missing scores for {name(c, s)}")
            vneg = np.array([sv[(p["id_a"], p["id_b"])] for p in val if p["label"] == 0])
            t = thr_at(vneg, 0.01)
            flags[(c, s)] = np.array([stt[(p["id_a"], p["id_b"])] > t for p in pos], dtype=float)
    rows = []
    for fam, fs in FAMS.items():
        m = np.array([p["family"] in fs for p in pos])
        out = {}
        for c in "AB":
            point = np.mean([flags[(c, s)][m].mean() for s in SEEDS])
            boot = np.mean([(W[:, m] * flags[(c, s)][m]).sum(1) / W[:, m].sum(1) for s in SEEDS], axis=0)
            out[c] = (point, boot)
        d_point, d_boot = out["B"][0] - out["A"][0], out["B"][1] - out["A"][1]
        per_seed_d = [flags[("B", s)][m].mean() - flags[("A", s)][m].mean() for s in SEEDS]
        rows.append({"family": fam, "n_pos": int(m.sum()),
                     "A_mean": out["A"][0], "A_lo": np.percentile(out["A"][1], 2.5), "A_hi": np.percentile(out["A"][1], 97.5),
                     "B_mean": out["B"][0], "B_lo": np.percentile(out["B"][1], 2.5), "B_hi": np.percentile(out["B"][1], 97.5),
                     "BminusA_mean": d_point, "BminusA_lo": np.percentile(d_boot, 2.5), "BminusA_hi": np.percentile(d_boot, 97.5),
                     "BminusA_per_seed": " / ".join(f"{100 * x:+.1f}" for x in per_seed_d)})
    with open(os.path.join(E, "seed_summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})
    held = next(r for r in rows if r["family"].startswith("deadcode"))
    signs = [float(x) for x in held["BminusA_per_seed"].split(" / ")]
    if all(v > 0 for v in signs):
        rule = "positive for every seed -> 'The held-out gain is positive for every seed but stays far below the seen-family gain.'"
    elif all(v < 0 for v in signs):
        rule = "negative for every seed -> 'augmentation did not help on the unseen family.'"
    else:
        rule = "mixed signs -> 'we cannot claim any transfer to the unseen family.'"
    with open(os.path.join(E, "seed_summary.md"), "w") as f:
        f.write(f"# Seed summary (final-pass Step 4)\n\nSeeds {SEEDS} (42 = main run, 'seed-0'). TPR (%) at the 1%-FPR validation threshold, JPlag-scorable test pairs. "
                f"Mean over seeds; 95% CI from {B} bootstrap resamples of test **problem IDs** ({len(pids)} problems), identical resamples across seeds and conditions.\n\n")
        f.write("| family | n_pos | A mean [95% CI] | B mean [95% CI] | B−A mean [95% CI] | B−A per seed (42/1/2) |\n|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['family']} | {r['n_pos']} | {100*r['A_mean']:.1f} [{100*r['A_lo']:.1f}, {100*r['A_hi']:.1f}] | "
                    f"{100*r['B_mean']:.1f} [{100*r['B_lo']:.1f}, {100*r['B_hi']:.1f}] | {100*r['BminusA_mean']:+.1f} "
                    f"[{100*r['BminusA_lo']:+.1f}, {100*r['BminusA_hi']:+.1f}] | {r['BminusA_per_seed']} |\n")
        f.write(f"\n**Fixed rule (paper/make_numbers.py, unchanged):** sign of per-seed held-out B−A TPR@1 → {rule}\n")
    print(open(os.path.join(E, "seed_summary.md")).read())


if __name__ == "__main__":
    main()
