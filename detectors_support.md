# Detector support for Python (Step 0)

| Detector | Python input? | Source checked | Version used | Invocation used here |
|---|---|---|---|---|
| **JPlag** | Yes, language module `python3` (README lists Python 3.6, ANTLR 4, "mature") | https://github.com/jplag/JPlag (README language table); `--help` lists subcommand `python3` | 6.3.0 jar (needs Java ≥ 25; run with Homebrew OpenJDK 27) | `java -jar tools/jplag.jar -l python3 -M RUN --csv-export -n -1 -t <T> -r <out> <rootdir>`, where each submission is a single `.py` file; the pairwise score is `AVG` similarity from the `.csv` export |
| **Dolos** | Yes (docs list "Python" as a supported language, parsed via tree-sitter) | https://dolos.ugent.be/about/languages.html | `@dodona/dolos` 2.10.0 (Node 24) | `dolos run -l python -f csv -o <outdir> <files...>`; the pairwise score is the `similarity` column of `pairs.csv` |
| **Moss** | Yes (Moss page: "C, C++, Java, C#, Python, ...") | https://theory.stanford.edu/~aiken/moss/ | — | **Skipped.** No Moss user ID was available (the user said "skip moss for now"). |

Smoke tests (2 tiny files differing only by identifiers): JPlag (`-t 3`) gave AVG = 1.0, and Dolos gave similarity = 1.0. Both tools ran successfully on Python input.

Notes:
- The npm package `@dodona/dolos-cli` doesn't exist; the CLI ships in `@dodona/dolos`. It was installed locally under `tools/dolos` with a local npm cache, because the user's global `~/.npm` cache has a root-owned-file permission problem.
- JPlag 6.3.0 is compiled for class file version 69 (Java 25). The system JDK 17 and the Homebrew JDK 21 both fail to run it, so OpenJDK 27 is used.
