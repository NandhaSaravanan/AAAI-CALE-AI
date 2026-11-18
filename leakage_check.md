# Leakage check (final-pass Step 2)

Source: data/programs.jsonl and data/pairs_{train,val,test}.jsonl; script data/leakage_check.py.

| check | items checked | violations | result |
|---|---|---|---|
| No problem ID in more than one split | 313 | 0 | PASS |
| No original program (problem+solution ID) in more than one split | 2448 | 0 | PASS |
| Every paired program's split label matches the pair file it appears in | 76880 | 0 | PASS |
| Dead-code programs appear only in the test split (train, val counts must be 0) | train 0, val 0, test 988 | 0 | PASS |
| No test pair whose two programs are identical after whitespace normalization | 8397 | 0 | PASS |

Pairs per split: train 26490, val 3553, test 8397

**Overall: ALL PASS**
