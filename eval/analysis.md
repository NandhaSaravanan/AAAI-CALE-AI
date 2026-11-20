# Post-hoc analysis (main run, seed 42, JPlag-scorable view; 1%-FPR validation thresholds)

## Held-out TPR@1% by insertion tercile

| bin | range | n | learned_0 | learned_A | learned_B | jplag | moss | dolos |
|---|---|---|---|---|---|---|---|---|
| 0 | 0.008–0.124 | 264 | 95.8 | 95.1 | 95.5 | 89.0 | 92.4 | 100.0 |
| 1 | 0.124–0.288 | 263 | 63.1 | 78.3 | 82.5 | 67.7 | 81.0 | 100.0 |
| 2 | 0.289–1.030 | 263 | 28.9 | 57.0 | 63.9 | 31.6 | 38.0 | 92.4 |

## Held-out TPR@1% by length tercile

| bin | range | n | learned_0 | learned_A | learned_B | jplag | moss | dolos |
|---|---|---|---|---|---|---|---|---|
| 0 | 33.000–64.000 | 268 | 36.6 | 61.2 | 67.2 | 25.0 | 30.6 | 92.5 |
| 1 | 65.000–109.000 | 260 | 60.4 | 80.4 | 83.5 | 67.7 | 81.9 | 100.0 |
| 2 | 110.000–634.000 | 262 | 91.6 | 89.3 | 91.6 | 96.6 | 100.0 | 100.0 |

## Realized test FPR (%) at the 1% threshold by negative type

| type | n | learned_0 | learned_A | learned_B | jplag | moss | dolos |
|---|---|---|---|---|---|---|---|
| hard_struct | 1101 | 3.3 | 2.9 | 2.4 | 3.1 | 2.4 | 4.5 |
| random | 1891 | 0.0 | 0.2 | 0.2 | 0.0 | 0.1 | 0.1 |

## Missed dead-code pairs (overlap)

- overlap:learned_B:dolos missed_a: 153 of 790
- overlap:learned_B:dolos missed_b: 20 of 790
- overlap:learned_B:dolos missed_both: 14 of 790
- overlap:learned_B:dolos missed_a_caught_b: 139 of 790
- overlap:learned_B:dolos missed_b_caught_a: 6 of 790
- overlap:learned_B:dolos caught_either: 776 of 790
- overlap:learned_B:jplag missed_a: 153 of 790
- overlap:learned_B:jplag missed_b: 294 of 790
- overlap:learned_B:jplag missed_both: 99 of 790
- overlap:learned_B:jplag missed_a_caught_b: 54 of 790
- overlap:learned_B:jplag missed_b_caught_a: 195 of 790
- overlap:learned_B:jplag caught_either: 691 of 790
- overlap:learned_B:moss missed_a: 153 of 790
- overlap:learned_B:moss missed_b: 233 of 790
- overlap:learned_B:moss missed_both: 82 of 790
- overlap:learned_B:moss missed_a_caught_b: 71 of 790
- overlap:learned_B:moss missed_b_caught_a: 151 of 790
- overlap:learned_B:moss caught_either: 708 of 790
