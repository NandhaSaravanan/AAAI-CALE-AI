# Dataset audit (Step 0)

**Requested dataset** `verifiers-for-code/CodeNet-16K` (Hugging Face): NOT AVAILABLE — Hub API returns 401 / not found and it does not appear in Hub search. Per the user's fallback, Project CodeNet (IBM) was used instead.

**Used**: `Project_CodeNet_Python800.tar.gz` (Python solutions) + `Project_CodeNet_metadata.tar.gz` (problem descriptions containing sample I/O), from the official download links in the IBM/Project_CodeNet README.

**License**: Project CodeNet repository is Apache-2.0 (LICENSE file in IBM/Project_CodeNet). Dataset is published by IBM for research use; we do not redistribute it.

- Problems in Python800: 800
- Solutions in Python800: 240000
- Problems with >=1 parsed (sample input, expected output) pair: **787**
- Parse outcome counts: {'no_samples_parsed': 13, 'ok': 787}
- Total sample pairs: 2193

Sample I/O comes from problem-description HTML ("Sample Input k"/"Sample Output k" blocks). Problems whose answers allow multiple correct outputs or float tolerance are filtered later because the original program must reproduce the expected output exactly (Step 2).
