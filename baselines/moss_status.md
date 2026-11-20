# Moss status (updated Fri Nov 20 2026)

Earlier (Nov 18): no registration reply; Moss was not evaluated.
Nov 20: the author received the Moss user ID. It is supplied only through the `MOSS_USERID` environment
variable at run time and is not stored in any file in this repository (checked with grep).

Run: `MOSS_USERID=... python baselines/run_moss.py` (Python client for the Moss socket protocol, same
150-pair chunks and input normalization as JPlag/Dolos; `-m 1000000`, `-n 100000`, language python).
Result: val 3,553/3,553 and test 8,397/8,397 pairs scored, 0 chunk failures (work/moss_run.log;
per-chunk result URLs cached in work/baselines/moss/). Score = mean of the two percent-matched values / 100;
pairs Moss does not list = 0. Existing results for all other detectors were verified unchanged after
re-running eval/evaluate.py (results.csv, deltas.csv, view_all/results.csv: 0 changed rows, only Moss rows added).
