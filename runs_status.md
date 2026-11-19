# Seed-run status (final-pass Step 0, Wed Nov 18 16:15:40 EST 2026)

Power: on **battery** (see env.txt); the Mac slept with the lid closed ~12:30–16:08 EST on 2026-11-18, stalling training (pmset log). Per the final-pass instructions, work stopped at Step 0 until the Mac is on power with the lid open.

| run | status | progress |
|---|---|---|
| seed 42 ("seed-0"), A | finished | model/train_log_A.jsonl, eval/scores/learned_A_*.jsonl |
| seed 42 ("seed-0"), B | finished | model/train_log_B.jsonl, eval/scores/learned_B_*.jsonl |
| seed 1, A | finished | model/train_log_A_s1.jsonl |
| seed 1, B | finished | model/train_log_B_s1.jsonl |
| seed 2, A | finished | model/train_log_A_s2.jsonl |
| seed 2, B | finished | model/train_log_B_s2.jsonl |

Runs are queued in one background job under `caffeinate -dimsu` (prevents idle sleep only; cannot prevent lid-closed sleep on battery). Estimated remaining awake time: ~3–3.5 h.

**Override (Wed Nov 18 16:28:54 EST 2026):** the user instructed to proceed on battery power. Seed runs continue; they stall whenever the lid is closed.

**Update (2026-11-18 19:52):** all four seed runs finished (no settings changed; 3 epochs each). eval/seeds.py run; its seed-42 ('seed-0') values match eval/results.csv exactly (12/12 values).
