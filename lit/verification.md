# Bibliography verification and novelty full-text check

Date: 2026-11-18. `lit/refs.bib` was left unchanged. I wrote a clean copy to `paper/refs.bib`: 40 entries, no `%` characters, braces balanced, and every key cited in `paper/main.tex` is present. The old `paper/refs.bib` had stray `,` lines (for example lines 1-4, and one inside `henkel2022semantic`), left behind when comments were stripped. Those are gone. BibTeX/biber is not installed on this machine, so the new file has not been compiled.

Sources: I took metadata from the Crossref REST API (`https://api.crossref.org/works/<DOI>`, publisher-deposited) and the arXiv API (`https://export.arxiv.org/api/query?id_list=...`). I also used the ACM-formatted author PDFs on arXiv. ACM DL (dl.acm.org) returned HTTP 403, and dblp blocked automated access (Anubis bot wall), so neither could be used.

## Task 1: flagged fields

| Key | Field | Old (lit/refs.bib) | New (paper/refs.bib) | Source |
|---|---|---|---|---|
| devore2020mossad | doi | 10.1145/3428206 (UNVERIFIED) | 10.1145/3428206 (confirmed: title, authors, PACMPL 4(OOPSLA), 2020) | https://api.crossref.org/works/10.1145/3428206 ; SIGPLAN OpenTOC https://sigplan.org/OpenTOC/oopsla20.html |
| devore2020mossad | articleno | 138 (UNVERIFIED) | **dropped**: no primary source reachable (ACM DL 403; Crossref has pages "1-28" only, no article number; the arXiv PDF has no ACM footer). One library catalog record (Summon, ersearch2.cvtisr.sk) lists ArticleNumber 138. That is secondary, so the field was not kept. | as stated |
| yefet2020adversarial | articleno | 162 (UNVERIFIED) | **dropped**: no primary or secondary source found. Crossref confirms DOI 10.1145/3428230, vol 4, OOPSLA, pages 1-30. Indirect evidence only: OOPSLA'20 DOIs look sequential (10.1145/3428243 is listed as Article 175 in a TU Delft repository record), which would make 3428230 Article 162 and 3428206 Article 138. That is inference, not verification. | https://api.crossref.org/works/10.1145/3428230 |
| cheers2021robustness | volume / number / articleno | 26 / 5 / 83 (UNVERIFIED) | 26 / 5 / 83 (confirmed) | https://api.crossref.org/works/10.1007/s10664-021-09990-4 |
| maertens2024dolos | volume | 26 (UNVERIFIED) | 26 (confirmed; article/page 101755, May 2024) | https://api.crossref.org/works/10.1016/j.softx.2024.101755 |
| zhang2023clonegen | volume / number / pages | missing (UNVERIFIED) | **added** volume 49, number 5, pages 3052--3070 | https://api.crossref.org/works/10.1109/TSE.2023.3240118 |
| uhm2026asmfooler | volume | 3 (UNVERIFIED) | 3 (confirmed) | Crossref https://api.crossref.org/works/10.1145/3797116 (vol 3, issue FSE) |
| uhm2026asmfooler | articleno | FSE088 (from citedrive) | FSE088 (confirmed from the ACM-formatted footer of the author PDF: "Proc. ACM Softw. Eng., Vol. 3, No. FSE, Article FSE088. Publication date: July 2026.", with doi 10.1145/3797116 on the same page) | https://arxiv.org/pdf/2602.12681 |
| puri2021codenet | author | 17 authors (UNVERIFIED) | unchanged: exact match with arXiv (same 17 names, same order) | https://arxiv.org/abs/2105.12655 |
| lu2021codexglue | author | "Lu, Shuai and Guo, Daya and others" | full 22-author list: Lu, Guo, Ren, Huang, Svyatkovskiy, Blanco, Clement, Drain, Jiang (Daxin), Tang (Duyu), Li (Ge), Zhou (Lidong), Shou, Zhou (Long), Tufano, Gong, Zhou (Ming), Duan, Sundaresan, Deng (Shao Kun), Fu, Liu (Shujie) | https://arxiv.org/abs/2102.04664 |
| jia2022funcfooler | author | "Jia, Lichen and others" | full 9-author list: Jia, Tang (Bowen), Wu (Chenggang), Wang (Zhe), Jiang (Zihan), Lai (Yuanming), Kang (Yan), Liu (Ning), Zhang (Jingfeng) | https://arxiv.org/abs/2208.14191 |

Other comment-flagged entries, checked while I was at it:

| Key | Issue | Result | Source |
|---|---|---|---|
| feng2020codebert | authors "from memory" | all 11 authors confirmed, same order | https://api.crossref.org/works/10.18653/v1/2020.findings-emnlp.139 |
| henkel2022semantic | author order (arXiv vs SANER) | the IEEE deposit lists Henkel first, in the order already in the file; kept | https://api.crossref.org/works/10.1109/SANER53432.2022.00070 |
| he2026invpt | venue string | arXiv comment reads "To appear in LMPL 2026"; booktitle kept as "LMPL 2026 (to appear)"; authors match arXiv | https://arxiv.org/abs/2608.15412 |
| schulze2013robustness, sonnekalb2022generalizability | "DOI not verified" | there was no DOI field to verify; only the comment was removed (not cited in main.tex) | none |
| all other DOIs in the file | sanity check | all resolve in Crossref with matching titles and authors. The JPlag JUCS DOI is registered with DataCite (https://api.datacite.org/dois/10.3217/jucs-008-11-1016) and resolves to lib.jucs.org | Crossref / DataCite |

## Task 2: full-text novelty check

Our claim: no prior study combines (a) training a learned similarity model on some semantics-preserving transformation families and testing on a held-out family, (b) comparison against token plagiarism tools (JPlag/Dolos/Moss), and (c) a matched-FPR operating point.

### Zubkov et al. 2022, arXiv 2206.08726 (read in full, v1)

- **(a) Held-out family? No.** The CodeTransformator dataset applies all nine transformations at random, and the split is random. Sec. 3.2 "Plagiarism Detection": "In this work, we apply all nine transformations with an equal probability of 0.3, which leads us to an average of three transformations per file. For each file, we create four augmented versions of it." Also: "We split the dataset into training, validation, and testing sets in the proportion of 60 : 20 : 20." No per-transformation or leave-one-family-out analysis appears anywhere.
- **(b) Token tools? Yes, JPlag (plus Simian and CCAligner).** Sec. 3.3 "Baselines": "We compare our models with several baselines, including a non-ML approach Simian, CCAligner [55], JPlag [43], and modern ML-based approaches Infercode [8] and Trans-Coder [30]." Also: "JPlag ... converts each program into a string of canonical tokens ... In our experiments, we used the tool with its default parameters." Sec. 5.3: "Overall, as expected, ML-based models significantly outperformed token-based Simian, CCAligner, and JPlag in both tasks." There is no Dolos and no Moss.
- **(c) Fixed-FPR operating point? No.** They use only threshold-free retrieval metrics, and the authors say so. Sec. 3.1 "Metrics": "[F-score] requires tuning the threshold, which is highly sensitive to each particular dataset [45]. Due to this fact, instead of tuning thresholds for F-score, we considered F-score@R ... we also considered Mean Average Precision at R (MAP@R)." Sec. 3.2: "we evaluate the trained models using F1@R and MAP@R ... we chose R to be equal to 5".
- **Note:** this is the closest prior work on (b). It trains contrastive models on transformed plagiarism-like data and benchmarks them against JPlag on the same transformations.

### Zhang et al. 2023, CloneGen (TSE 49(5)), arXiv 2111.10793 v1 (read in full; the published TSE version may differ)

- **(a) Held-out family? No.** Detectors are trained on untransformed OJClone and tested on transformed sets. Adversarial retraining then mixes data from all strategies, and therefore all 15 operators. Sec. 6.2 "RQ1": "we use the initial datasets DI as the training dataset for three assessed detectors. Then, for each different strategy, we use the corresponding generated dataset (DRS, DGA, DMCMC, DDRL) as the testing dataset." Sec. 6.3 "RQ2": "we use the following datasets as the training dataset: DI + 25%D′RS + 25%D′GA + 25%D′MCMC + 25%D′DRL ... Due to randomness of these strategies, the new generated datasets (e.g., D′RS) will not be identical to the testing datasets (e.g., DRS)." In Sec. 6.4 "RQ3" the operators are split into a semantic group and an obfuscation group (DSem and DObf). But the "Adversarial" model there is trained on the same all-operator mixture, so neither group is held out of training. The held-out element is fresh samples, not an unseen family.
- **(b) Token tools? Traditional clone detectors only, not plagiarism tools.** Sec. 6.5 "RQ4": "we conduct a set of experiments with four open-source detectors as SOURCERERCC [55], DECKARD [11], CCALIGNER [10], NICAD [57]." Moss is named only as future work. Sec. 7.1 "Threats to Validity": "In the future, we would like to support more ML-based detectors ... or even code plagiarism tools such as MOSS [58]." There is no JPlag and no Dolos.
- **(c) Fixed-FPR operating point? No.** Sec. 6.1.4 "Evaluation Metrics": "We use Precision (P), Recall (R) and F1-Measure (F1) Score to measure the performance of the ML-based detector." Also: "We use Recall (R) to measure the performance of traditional tools on detecting code clones." Traditional tools run at their default decisions ("we use their default settings", Sec. 7.1), and ML models at their classifier outputs. Thresholds are not matched across tools.

### He et al. 2026, InvPT, arXiv 2608.15412 v1 (read in full)

- **(a) Held-out family? No. They hold out compositions and a language, not a family, and they say so explicitly.** The quotes below are exact:
  - Abstract: "Because the transformed test sets compose the same operator family used in pretraining, we claim invariance to that family rather than robustness in general."
  - Sec. 3.3 "Robustness Against Invariant Programs": "We evaluate robustness by cumulatively applying all six transformations from Section 2.1 to the test set. Because training uses only single-operator transformations, these compositions are unseen, so the setting measures invariance to the pretraining rewrite family under novel compositions rather than robustness to arbitrary semantics-preserving edits (Section 5)."
  - Sec. 5 "Limitations": "Our robustness evaluation uses test-time compositions that are unseen but built from the same six operators used in pretraining. The results therefore establish invariance to this rewrite family, not robustness to semantics-preserving change in general; independently generated transformations and naturally occurring refactorings remain untested."
  - Sec. 6 "Conclusion": "These gains recover part of the degradation, not most of it, and are measured on compositions of the operator family seen in pretraining; robustness to structurally different rewrites remains open."
  - What they do hold out is a language. Sec. 3.1: "We hold C/C++ out of pretraining on purpose." Sec. 3.3 also mentions "a held-out target language".
- **(b) Token tools? No.** The baselines are encoders only (Sec. 3.1): "We compare CodeBERT [5], GraphCodeBERT [6], ContraBERT_C, and ContraBERT_G [13], together with their InvPT counterparts", plus CodeSage and ModernBERT as reference points. JPlag, Dolos, Moss and other token tools are never mentioned.
- **(c) Fixed-FPR operating point? No.** Sec. 3.1: "For clone detection, we report Mean Average Precision at R (MAP@R) [36], and for code classification we report accuracy."

So, yes: InvPT states plainly that its test transforms come from the same family used in pretraining, and that unseen or structurally different rewrite families remain open. The quotes above (Abstract, Sec. 3.3, Sec. 5, Sec. 6) can be cited verbatim.

## Verdict on the novelty sentence

"found no study combining a held-out family, learned and token detectors, and a matched-FPR operating point"

**It is safe for these three papers, but soften the scope slightly.**

- None of the three has (a) a held-out family.
- None has (c) a matched or fixed FPR.
- Only Zubkov has (b): learned models against JPlag on transformed code.
- CloneGen compares against token clone detectors such as SourcererCC, but not plagiarism tools.

The sentence as a conjunction is therefore accurate. Because "found no study" depends on how far the search went, phrase it as "to our knowledge" or "in the work we surveyed". Also acknowledge that Zubkov et al. already compared contrastive models with JPlag on plagiarism-style transformations, and that InvPT explicitly leaves unseen families open.
