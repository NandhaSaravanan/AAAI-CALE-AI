# Seed summary (final-pass Step 4)

Seeds [42, 1, 2] (42 = main run, 'seed-0'). TPR (%) at the 1%-FPR validation threshold, JPlag-scorable test pairs. Mean over seeds; 95% CI from 1000 bootstrap resamples of test **problem IDs** (59 problems), identical resamples across seeds and conditions.

| family | n_pos | A mean [95% CI] | B mean [95% CI] | B−A mean [95% CI] | B−A per seed (42/1/2) |
|---|---|---|---|---|---|
| rename | 778 | 45.4 [36.8, 54.5] | 90.4 [86.2, 94.5] | +45.0 [+37.2, +52.7] | +47.6 / +49.4 / +38.2 |
| reorder | 253 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] | +0.0 / +0.0 / +0.0 |
| deadcode (held-out) | 790 | 76.2 [70.6, 81.8] | 79.2 [73.8, 84.5] | +3.0 [+1.2, +5.0] | +3.8 / +6.5 / -1.3 |
| seen pooled | 1031 | 58.8 [52.0, 65.6] | 92.8 [89.5, 95.8] | +34.0 [+28.1, +39.9] | +35.9 / +37.2 / +28.8 |
| same_problem | 1241 | 64.1 [58.0, 71.4] | 62.8 [56.5, 69.9] | -1.3 [-5.6, +3.1] | -0.8 / +1.0 / -4.1 |

**Fixed rule (paper/make_numbers.py, unchanged):** sign of per-seed held-out B−A TPR@1 → mixed signs -> 'we cannot claim any transfer to the unseen family.'
