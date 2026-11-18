## Step 4: first training launch failed
- NotImplementedError: scaled_dot_product_attention for MPS does not support dropout. Fix: attention_probs_dropout_prob=0.0 (hidden dropout kept). Relaunched.
## Step 5: JPlag hang
- JPlag 6.3.0 spectral clustering threw MaxCountExceededException (convergence failed) on some 150-pair chunks; main thread died but a non-daemon IdleBar thread kept the JVM alive, so the run hung until the 1800 s timeout and the script crashed (TimeoutExpired). Fix: --cluster-skip (clustering does not affect pairwise similarity), 600 s timeout caught; finished chunks reused.
## Step 0: environment / data
- HF dataset `verifiers-for-code/CodeNet-16K`: Hub API 401 / not in search -> does not exist. Fallback (user-listed): IBM Project CodeNet Python800 + metadata (problem descriptions with sample I/O).
- `npm install @dodona/dolos-cli`: 404 (package does not exist); the CLI ships in `@dodona/dolos`. Second attempt failed on root-owned files in ~/.npm cache -> installed with a local `--cache`.
- JPlag 6.3.0 jar: UnsupportedClassVersionError on JDK 17 and JDK 21 (needs class version 69 = Java 25) -> Homebrew OpenJDK 27.
## Step 2: transform bug caught by the execution check
- deadcode inserted snippets before an `elif` line, breaking the if/elif chain (2 mismatches in a 20-problem trial). Fixed (skip `elif` positions) before the full run; full run: 0 failing variants.
## Step 5: JPlag parsing
- ANTLR python3 grammar rejected files without a final newline / with indented trailing blank lines -> whitespace-only normalization (rstrip lines, single final newline) for both baseline tools.
- JPlag rejects submissions with fewer tokens than its default min match (12): 27.9% of test pairs unscored -> main analysis on JPlag-scorable pairs for all detectors; all-pairs view (unscored = 0) in eval/view_all/.
## Step 4: machine sleep
- Mac on battery in Low Power Mode with 1-min sleep timer: condition B's wall clock was 534 min instead of ~75 (training resumed correctly after each sleep; results unaffected). `caffeinate -dimsu` added. Do not cite B's wall-clock time.
## Step 7: LaTeX
- AAAI-27 style requires pdfTeX (`\RequirePDFTeX`); no pdfLaTeX installed. Installing TinyTeX was denied by the permission system (not retried). Preview built with tectonic via `paper/preview_xetex.tex`, which disables that guard; the submission PDF must be compiled with pdfLaTeX (e.g. Overleaf).
- First tectonic build failed: DNS error fetching its package bundle (transient; machine was offline/asleep). Retry succeeded.
- lit/refs.bib had `% UNVERIFIED` comments inside entries, which BibTeX swallows into fields (years printed as ????). paper/refs.bib is a copy with those comments stripped; the notes are kept in lit/refs.bib.
## Final pass Step 5: reproduction mismatch
- Clean re-run of verify/run_check.py produced different verify_report.csv / work/programs.jsonl (2,443 vs 2,448 originals kept) because the 5 s wall-clock timeout fired more often under CPU load (21 vs 6 original timeouts) while seed training ran on battery. Transforms are deterministic (13,540 common programs byte-identical); build_pairs.py is hash-identical given the original verified programs. Originals not overwritten. Details: reproduction_check.md.
