# Literature search log

Date: 2026-11-17. Tools: WebSearch (standard/extended) + WebFetch on arXiv / ACL Anthology / researchr landing pages.
"Verified" = title/authors/venue confirmed on at least one primary landing page (arXiv, ACL Anthology, publisher, conference site, DBLP) or two consistent indexes.

## Bucket 1: binary code similarity robustness

1. `asmFooler binary code similarity semantics-preserving transformations`
   - Fool Me If You Can: On the Robustness of Binary Code Similarity Detection Models against Semantics-preserving Transformations (Uhm et al., FSE 2026) - https://arxiv.org/abs/2602.12681
   - DOI listing 10.1145/3797116 (PACMSE FSE) - https://www.citedrive.com/en/discovery/fool-me-if-you-can-on-the-robustness-of-binary-code-similarity-detection-models-against-semantics-preserving-transformations/
2. `adversarial attacks against binary similarity systems Capozzi`
   - Adversarial Attacks against Binary Similarity Systems (Capozzi et al., IEEE Access 2024) - https://arxiv.org/abs/2303.11143 ; https://doi.org/10.1109/ACCESS.2024.3488204
3. `FuncFooler practical black-box attack learning-based binary code similarity detection`
   - FuncFooler (Jia et al., arXiv 2022) - https://arxiv.org/abs/2208.14191

## Bucket 2: source-level plagiarism detection robustness

4. `Sağlam automated obfuscation attacks JPlag software plagiarism detection defense`
   - Evaluating Software Plagiarism Detection in the Age of AI (Sağlam & Schmid, arXiv 2025) - https://arxiv.org/abs/2505.20158
   - KIT repository hits (thesis / companion papers) - https://publikationen.bibliothek.kit.edu/1000167858/152125267
5. `"Automated Detection of AI-Obfuscated Plagiarism" OR "Token Sequence Normalization" Sağlam ICSE 2024 JPlag`
   - Detecting Automatic Software Plagiarism via Token Sequence Normalization (ICSE 2024) - https://conf.researchr.org/details/icse-2024/icse-2024-artifact-evaluation/42/Detecting-Automatic-Software-Plagiarism-via-Token-Sequence-Normalization
6. `Sağlam "Obfuscation-Resilient Software Plagiarism Detection with JPlag" ICSE companion`
   - ICSE 2024 poster - https://conf.researchr.org/details/icse-2024/icse-2024-posters/11/Obfuscation-Resilient-Software-Plagiarism-Detection-with-JPlag ; IEEE Xplore https://ieeexplore.ieee.org/document/10554978
7. `Sağlam "Automated Detection of AI-Obfuscated Plagiarism in Modeling Assignments" ICSE SEET 2024 authors DOI`
   - https://conf.researchr.org/details/icse-2024/icse-2024-software-engineering-education-and-training-track/35/Automated-Detection-of-AI-Obfuscated-Plagiarism-in-Modeling-Assignments
8. `Mossad defeating software plagiarism detection Devore-McDonald Berger OOPSLA 2020`
   - https://arxiv.org/abs/2010.01700 ; https://2020.splashcon.org/details/splash-2020-oopsla/14/Mossad-Defeating-Software-Plagiarism-Detection
9. `ChatGPT LLM obfuscation source code plagiarism detection evasion MOSS JPlag Dolos study`
   - Fooling MOSS Detection with Pretrained Language Models (Biderman & Raff, CIKM 2022) - https://arxiv.org/abs/2201.07406
   - ASEE paper on ChatGPT + IEEEXtreme obfuscation - https://peer.asee.org/45088.pdf (PDF could not be parsed; NOT verified, not cited)
10. `Biderman Raff "Fooling MOSS detection with pretrained language models" CIKM 2022` - confirmed DOI 10.1145/3511808.3557079
11. `ASEE 2023 ChatGPT obfuscation plagiarism detection MOSS programming assignments paper` - same ASEE PDF; metadata unverifiable -> excluded
12. `Ragkhitwetsagul Krinke Clark "A comparison of code similarity analysers" Empirical Software Engineering 2018`
    - https://cragkhit.github.io/publications/cloplag_emse.pdf ; DBLP https://dblp.org/rec/bibtex/journals/ese/Ragkhitwetsagul18
13. `Schulze Meyer "On the robustness of clone detection to code obfuscation" IWSC 2013`
    - DBLP IWSC 2013 - https://dblp.org/db/conf/iwsc/iwsc2013.html
    - Evaluating the robustness of source code plagiarism detection tools to pervasive plagiarism-hiding modifications (Cheers et al.) - https://arxiv.org/abs/2102.03997
14. `Cheers Lin Smith "Evaluating the robustness ..." Empirical Software Engineering 2021` - DOI 10.1007/s10664-021-09990-4
15. `deep learning source code plagiarism detection compared with JPlag MOSS obfuscation pre-trained model`
    - Source Code Plagiarism Detection with Pre-Trained Model Embeddings and AutoML (Ebrahim & Joy, RANLP 2023) - https://aclanthology.org/2023.ranlp-1.34/
16. `learned code embedding plagiarism detector versus JPlag Dolos obfuscated submissions evaluation 2024 2025 arXiv` (extended)
    - Can Code Evaluation Metrics Detect Code Plagiarism? (Ebrahim & Joy, 2026) - https://arxiv.org/abs/2604.25778
    - Same Same But Different: Preventing Refactoring Attacks on Software Plagiarism Detection (Maisch et al., ICSE 2026) - https://arxiv.org/abs/2510.25057
    - The Failure of Plagiarism Detection in Competitive Programming (Dickey, arXiv 2025) - https://arxiv.org/abs/2505.08244
17. `ConPlag dataset contrastive plagiarism detection source code CodeBERT Slobodkin`
    - Towards a Dataset of Programming Contest Plagiarism in Java (Slobodkin & Sadovnikov) - https://arxiv.org/abs/2303.10763
    - Evaluation of Contrastive Learning with Various Code Representations for Code Clone Detection (Zubkov et al., 2022) - https://arxiv.org/abs/2206.08726
18. `dead code insertion plagiarism detection token-based robustness unseen obfuscation neural siamese CodeNet Python`
    - No direct hit; only the KIT JPlag line (TSN explicitly targets dead-code insertion + reordering) and Nocte (2510.25057).

## Bucket 3: tools

19. `"Winnowing: local algorithms for document fingerprinting" Schleimer Wilkerson Aiken SIGMOD 2003`
    - https://doi.org/10.1145/872757.872770 ; https://bibtex.github.io/SIGMOD-2003-SchleimerWA.html
20. `Prechelt Malpohl Philippsen "Finding plagiarisms among a set of programs with JPlag" J. UCS 2002`
    - https://www.jucs.org/jucs_8_11/finding_plagiarisms_among_a/Prechelt_L.html ; DOI 10.3217/jucs-008-11-1016
21. `Dolos language-agnostic plagiarism detection source code Maertens 2022 Journal of Computer Assisted Learning`
    - DOI 10.1111/jcal.12662 ; Dolos 2.0 arXiv https://arxiv.org/abs/2402.10853 (SoftwareX DOI 10.1016/j.softx.2024.101755)

## Bucket 4: learned code models, benchmarks, robustness

22. `UniXcoder unified cross-modal pre-training for code representation ACL 2022 Guo` - https://aclanthology.org/2022.acl-long.499
23. `CodeBERT pre-trained model programming natural languages Findings EMNLP 2020 Feng` - https://aclanthology.org/2020.findings-emnlp.139
24. `CodeNet large-scale AI for code dataset Puri NeurIPS 2021 Datasets and Benchmarks` - https://arxiv.org/abs/2105.12655
25. `Lu et al. CodeXGLUE ...` - https://arxiv.org/abs/2102.04664 ; NeurIPS D&B proceedings PDF
26. `Mou ... TBCNN AAAI 2016 POJ-104` - https://ojs.aaai.org/index.php/AAAI/article/view/10139
27. `Svajlenko Roy ... BigCloneBench ICSME 2014` - https://dblp.uni-trier.de/rec/conf/icsm/SvajlenkoIKRM14.html
28. `Yefet Alon Yahav "Adversarial examples for models of code" OOPSLA 2020` - https://arxiv.org/abs/1910.07517
29. `Rabin "On the generalizability of neural program models ..." IST 2021` - https://arxiv.org/abs/2008.01566 ; DOI 10.1016/j.infsof.2021.106552
30. `Bielik Vechev "Adversarial robustness for code" ICML 2020` - https://proceedings.mlr.press/v119/bielik20a.html
31. `Henkel "Semantic Robustness of Models of Source Code" SANER 2022` - https://arxiv.org/abs/2002.03043
32. `Jain ... "Contrastive Code Representation Learning" EMNLP 2021` - https://aclanthology.org/2021.emnlp-main.482
33. `Corder self-supervised contrastive learning ... SIGIR 2021` - https://arxiv.org/abs/2009.02731
34. `Yang Shi He Lo "Natural attack for pre-trained models of code" ICSE 2022 ALERT` - https://arxiv.org/abs/2201.08698
35. `Sonnekalb generalizability of code clone detection on CodeBERT ASE 2022` - https://arxiv.org/abs/2208.12588
36. `contrastive learning code clone detection robustness unseen semantic-preserving transformation types out-of-distribution evaluation`
    - Invariant Pretraining for Robust Code Representations (He et al., LMPL 2026) - https://arxiv.org/abs/2608.15412
    - Challenging Machine Learning-based Clone Detectors via Semantic-preserving Code Transformations (CloneGen, TSE 2023) - https://arxiv.org/abs/2111.10793
37. `"leave-one-out" transformation clone detection code models robustness held-out obfuscation generalization` (extended)
    - Auto-SPT (Hooda et al., arXiv 2025) - https://arxiv.org/abs/2512.06042
    - A Unified Model for Cross-Domain Clone Detection via Model Merging (Roy et al., ASE 2026) - https://arxiv.org/abs/2608.04215

## Bucket 5: close prior work (novelty check)

Queries 16, 18, 36, 37 plus `neural code clone detection generalization unseen obfuscation types held-out transformation plagiarism JPlag Dolos comparison` (extended).
- No paper found that (a) trains a learned similarity model on some transformation families, (b) evaluates on a held-out family, AND (c) compares against JPlag/Dolos/Moss at a matched FPR.
- Nearest neighbours: CloneGen (learned + traditional detectors under 15 SPT operators, adversarial retraining; no leave-family-out, no JPlag/Dolos), Zubkov et al. 2022 (contrastive models vs "traditional tools" on plagiarism-like transformed competitive-programming data; held-out protocol not stated on abstract page), Ebrahim & Joy 2023/2026 (pretrained embeddings / metrics vs JPlag/Dolos on SOCO/ConPlag/IRPlag; no transformation-family generalization), InvPT 2026 (authors explicitly state test transforms are from the same operator family as pretraining), Sağlam et al. line (token-based JPlag defenses vs MOSS/Dolos; no learned models), asmFooler (binary-level).

Excluded / not verified: ASEE PDF (peer.asee.org/45088), KIT PDFs 1000167446 / 1000165371 (binary PDF, metadata unreadable), Karnalim et al. 2025 ML detector (only a secondary mention), "Are our clone detectors good enough?" (Cybersecurity 2023; redirect, not fetched).
