# Splits and pairs (Step 3)

Split unit: problem ID (70/10/20 by problem, seed 7); every original and all of its variants are in one split.

Train families: ['rename', 'reorder']. Held-out family: ['deadcode'] (test split only; never in train/val).

Negatives per original: up to 4 hard_struct (top token-structure 4-gram Jaccard, different problem) + 6 random different-problem.

Not built: same-problem semantically-different negatives (Python800 has only Accepted solutions).

| split | problems | originals | label | family | pair_type | count |
|---|---|---|---|---|---|---|
| train | 220 | 1716 | 0 | negative | hard_struct | 5849 |
| train | 220 | 1716 | 0 | negative | random | 10248 |
| train | 220 | 1716 | 1 | rename | transform | 3366 |
| train | 220 | 1716 | 1 | reorder | transform | 1074 |
| train | 220 | 1716 | 1 | same_problem | same_problem | 5953 |
| train | | | | **total** | | **26490** |
| val | 31 | 238 | 0 | negative | hard_struct | 752 |
| val | 31 | 238 | 0 | negative | random | 1375 |
| val | 31 | 238 | 1 | rename | transform | 468 |
| val | 31 | 238 | 1 | reorder | transform | 140 |
| val | 31 | 238 | 1 | same_problem | same_problem | 818 |
| val | | | | **total** | | **3553** |
| test | 62 | 494 | 0 | negative | hard_struct | 1565 |
| test | 62 | 494 | 0 | negative | random | 2913 |
| test | 62 | 494 | 1 | deadcode | transform | 988 |
| test | 62 | 494 | 1 | rename | transform | 952 |
| test | 62 | 494 | 1 | reorder | transform | 256 |
| test | 62 | 494 | 1 | same_problem | same_problem | 1723 |
| test | | | | **total** | | **8397** |
