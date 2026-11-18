# Clean reproduction (final-pass Step 5)

Fresh `git clone` of the committed repo into the session scratchpad (outside the working directory); raw CodeNet archives symlinked read-only; originals were not touched. CPU stages re-run: `step0/audit_dataset.py`, `verify/run_check.py --problems 320 --per_problem 8`, `data/build_pairs.py`. Run concurrently with seed training on battery (Low Power Mode).

| file | result |
|---|---|
| data/samples.json | MATCH |
| dataset_audit.md | MATCH |
| verify_report.csv | MISMATCH |
| work/originals_status.json | MISMATCH |
| work/programs.jsonl | MISMATCH |
| data/programs.jsonl, data/pairs_{train,val,test}.jsonl, data/split_report.md | MISMATCH (inherited) |

**Cause.** Wall-clock 5 s execution timeouts. Under CPU load, timeouts rose from 6 to 21 originals (and 17 variants timed out). 2,443 originals were kept instead of 2,448 (60 programs only in the original run, 15 only in the reproduction). The transforms themselves are deterministic: all 13,540 programs present in both runs are **byte-identical**.

**Isolation test.** Re-running `data/build_pairs.py` in the clean copy on the *original* `work/programs.jsonl` reproduces data/programs.jsonl, all three pair files, and split_report.md **hash-identically**. The split and pair construction is deterministic, and the only non-determinism is the timeout-based execution filter.

**Implication.** The committed dataset is the one used for every result. Exact regeneration needs an unloaded machine, or a CPU-time limit (instead of wall-clock) for the 5 s timeout. This is noted as a reproducibility limitation.
