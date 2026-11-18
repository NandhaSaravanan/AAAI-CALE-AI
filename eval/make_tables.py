"""Final-pass Step 3: per-family matched-FPR tables. Threshold per detector at 1% FPR on validation
negatives (evaluate.py); TPR on test per family. Main = JPlag-scorable view (eval/results.csv);
supplementary = all pairs, JPlag-unscorable pairs scored 0 (eval/view_all/results.csv)."""
import csv, os
EXP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COLS = ["detector", "family", "n_pos", "n_neg", "thr@1", "tpr@1", "tpr@1_lo", "tpr@1_hi", "test_fpr@1", "auc", "auc_lo", "auc_hi"]
FAM = {"rename": "rename (seen)", "reorder": "reorder (seen)", "deadcode": "deadcode (held-out)",
       "same_problem": "same_problem (reference)", "seen": "seen families pooled", "heldout": "held-out pooled"}
for src, dst in [("eval/results.csv", "eval/main_table.csv"), ("eval/view_all/results.csv", "eval/supplementary_table.csv")]:
    rows = list(csv.DictReader(open(os.path.join(EXP, src))))
    with open(os.path.join(EXP, dst), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in rows:
            w.writerow([r["detector"], FAM[r["subset"]]] + [r[c] for c in COLS[2:]])
    print(dst, len(rows), "rows")
