# Seed robustness (JPlag-scorable view), seeds = [1, 2, 42]

TPR in %, AUC raw. mean ± s.d. over seeds; per-seed values in seeds.csv.

| subset | metric | A | B | B − A | B − A per seed |
|---|---|---|---|---|---|
| seen | tpr@1 | 58.8 ± 5.4 | 92.8 ± 1.1 | 34.0 ± 4.5 | 35.9, 37.2, 28.8 |
| seen | tpr@5 | 81.1 ± 1.9 | 99.1 ± 0.3 | 18.0 ± 1.9 | 19.7, 18.3, 16.0 |
| seen | auc | 0.969 ± 0.002 | 0.997 ± 0.000 | 0.028 ± 0.002 | 0.030, 0.029, 0.025 |
| heldout | tpr@1 | 76.2 ± 8.9 | 79.2 ± 5.2 | 3.0 ± 3.9 | 3.8, 6.5, -1.3 |
| heldout | tpr@5 | 92.7 ± 2.9 | 92.7 ± 1.8 | 0.1 ± 1.4 | -1.0, 1.6, -0.4 |
| heldout | auc | 0.985 ± 0.006 | 0.988 ± 0.002 | 0.003 ± 0.004 | 0.001, 0.007, 0.001 |
