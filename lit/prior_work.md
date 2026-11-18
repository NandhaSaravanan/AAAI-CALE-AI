# Prior work (verified)

Study: fine-tuned UniXcoder siamese encoder vs JPlag / Dolos (Moss not run) on CodeNet Python800; train families = identifier renaming + statement reordering; held-out family = dead-code insertion; comparison at matched FPR.

Each entry: citation, URL, summary, how our study differs. [bib key] in brackets. Fields flagged "(unverified)" are from memory and should be checked before camera-ready.

---

## 1. Binary code similarity robustness

**[uhm2026asmfooler]** Jiyong Uhm, Minseok Kim, Michalis Polychronakis, Hyungjoon Koo. "Fool Me If You Can: On the Robustness of Binary Code Similarity Detection Models against Semantics-preserving Transformations." Proc. ACM Softw. Eng. (FSE 2026), DOI 10.1145/3797116. arXiv:2602.12681.
URL: https://arxiv.org/abs/2602.12681
Summary: asmFooler applies 8 semantics-preserving binary transformations (9,565 variants from 620 samples) to 6 deep BCSD models; robustness depends on pre-processing/architecture/features; small perturbations cause both FNs and FPs.
Differs: binary/assembly level and attack-oriented; we study source-level Python, a train/held-out transformation-family split, and token-based plagiarism baselines.

**[capozzi2024adversarial]** Gianluca Capozzi, Daniele Cono D'Elia, Giuseppe Antonio Di Luna, Leonardo Querzoni. "Adversarial Attacks against Binary Similarity Systems." IEEE Access 12:161247-161269, 2024. DOI 10.1109/ACCESS.2024.3488204.
URL: https://arxiv.org/abs/2303.11143
Summary: black-box (Spatial Greedy) and white-box attacks via instruction insertion on Gemini, GMN, SAFE; all are vulnerable.
Differs: adversarially optimized binary attacks; we measure distribution shift to an unseen, non-adversarial source transformation family.

**[jia2022funcfooler]** Lichen Jia et al. "FuncFooler: A Practical Black-box Attack Against Learning-based Binary Code Similarity Detection Methods." arXiv:2208.14191, 2022.
URL: https://arxiv.org/abs/2208.14191
Summary: inserts benign adversarial instructions (CFG- and semantics-preserving) to fool SAFE, Asm2Vec, jTrans.
Differs: same as above (binary, adversarial); our held-out family is plain dead-code insertion at source level.

## 2. Source-level plagiarism detection robustness / evaluation

**[devore2020mossad]** Breanna Devore-McDonald, Emery D. Berger. "Mossad: Defeating Software Plagiarism Detection." Proc. ACM Program. Lang. 4(OOPSLA), 2020.
URL: https://arxiv.org/abs/2010.01700
Summary: genetic-programming-style source transformations (mainly statement insertion) defeat Moss, JPlag and two other detectors; output judged as readable as student code.
Differs: attack on token detectors only; we include a learned model and ask about generalization to an unseen family. Mossad-style insertion is essentially our held-out dead-code family.

**[saglam2024tsn]** Timur Sağlam, Moritz Brödel, Larissa Schmid, Sebastian Hahner. "Detecting Automatic Software Plagiarism via Token Sequence Normalization." ICSE 2024. DOI 10.1145/3597503.3639192.
URL: https://conf.researchr.org/details/icse-2024/icse-2024-artifact-evaluation/42/Detecting-Automatic-Software-Plagiarism-via-Token-Sequence-Normalization
Summary: builds a token dependency graph to remove dead/inserted statements and canonicalize order in JPlag, reverting insertion and reordering attacks.
Differs: hand-engineered defense for exactly our held-out (dead code) and one train family (reordering); no learned model. IMPORTANT: JPlag >= 5 may include this normalization, which makes JPlag a strong baseline specifically on dead-code insertion; report the JPlag version and whether normalization is enabled.

**[saglam2024jplag]** Timur Sağlam, Sebastian Hahner, Larissa Schmid, Erik Burger. "Obfuscation-Resilient Software Plagiarism Detection with JPlag." ICSE-Companion 2024 (poster). DOI 10.1145/3639478.3643074.
URL: https://conf.researchr.org/details/icse-2024/icse-2024-posters/11/Obfuscation-Resilient-Software-Plagiarism-Detection-with-JPlag
Summary: JPlag extensions give broad resilience to automated obfuscation; reports JPlag well ahead of MOSS and Dolos under insertion/reordering.
Differs: token-based only; Java datasets.

**[saglam2025evaluating]** Timur Sağlam, Larissa Schmid. "Evaluating Software Plagiarism Detection in the Age of AI: Automated Obfuscation and Lessons for Academic Integrity." arXiv:2505.20158, 2025.
URL: https://arxiv.org/abs/2505.20158
Summary: two JPlag defenses evaluated against algorithmic and GPT-4-based obfuscation, >4M pairwise comparisons; defenses also help with AI-generated plagiarism.
Differs: no learned detector; no train/held-out family split.

**[maisch2026refactoring]** Robin Maisch, Larissa Schmid, Timur Sağlam, Nils Niehues. "Same Same But Different: Preventing Refactoring Attacks on Software Plagiarism Detection." ICSE 2026. DOI 10.1145/3744916.3773225. arXiv:2510.25057.
URL: https://arxiv.org/abs/2510.25057
Summary: code-property-graph framework (Nocte) to resist refactoring-based obfuscation, evaluated on student submissions with algorithmic and AI attacks.
Differs: graph/rule-based defense; we evaluate learned vs token detectors under family shift.

**[saglam2024modeling]** Timur Sağlam, Sebastian Hahner, Larissa Schmid, Erik Burger. "Automated Detection of AI-Obfuscated Plagiarism in Modeling Assignments." ICSE-SEET 2024. DOI 10.1145/3639474.3640084.
URL: https://conf.researchr.org/details/icse-2024/icse-2024-software-engineering-education-and-training-track/35/Automated-Detection-of-AI-Obfuscated-Plagiarism-in-Modeling-Assignments
Summary: plagiarism detection for EMF models, evaluated against ChatGPT-obfuscated plagiarism.
Differs: modeling artifacts, not source code. Optional citation (ChatGPT-obfuscation context).

**[biderman2022fooling]** Stella Biderman, Edward Raff. "Fooling MOSS Detection with Pretrained Language Models." CIKM 2022, pp. 2933-2943. DOI 10.1145/3511808.3557079.
URL: https://arxiv.org/abs/2201.07406
Summary: GPT-J solutions to intro assignments are not flagged by MOSS.
Differs: LLM-generated code vs MOSS; we use controlled rule-based transformations and matched-FPR comparison.

**[cheers2021robustness]** Hayden Cheers, Yuqing Lin, Shamus P. Smith. "Evaluating the robustness of source code plagiarism detection tools to pervasive plagiarism-hiding modifications." Empirical Software Engineering, 2021. DOI 10.1007/s10664-021-09990-4.
URL: https://arxiv.org/abs/2102.03997
Summary: 11 tools on simulated undergraduate plagiarism; none robust to fine-grained structural changes; JPlag and Plaggie most robust.
Differs: no learned model; no held-out family.

**[ragkhitwetsagul2018comparison]** Chaiyong Ragkhitwetsagul, Jens Krinke, David Clark. "A comparison of code similarity analysers." Empirical Software Engineering 23(4):2464-2519, 2018. DOI 10.1007/s10664-017-9564-7.
URL: https://cragkhit.github.io/publications/cloplag_emse.pdf
Summary: 30 similarity analysers (clone + plagiarism tools, incl. JPlag, Moss) under pervasive modifications/obfuscation; tuned configs transfer poorly across datasets.
Differs: pre-neural; finding that thresholds don't transfer motivates our matched-FPR protocol.

**[schulze2013robustness]** Sandro Schulze, Daniel Meyer. "On the robustness of clone detection to code obfuscation." IWSC 2013, pp. 62-68.
URL: https://dblp.org/db/conf/iwsc/iwsc2013.html
Summary: early study of clone-detector recall under obfuscation (renaming etc.). (Content known only from secondary descriptions.)
Differs: traditional clone detectors, Java/C.

**[dickey2025failure]** Ethan Dickey. "The Failure of Plagiarism Detection in Competitive Programming." arXiv:2505.08244, 2025.
URL: https://arxiv.org/abs/2505.08244
Summary: experience report; Moss-style checkers defeated by simple transformations and AI-generated code.
Differs: position/experience paper, no controlled experiment. Optional.

## 3. Tools

**[schleimer2003winnowing]** Saul Schleimer, Daniel S. Wilkerson, Alex Aiken. "Winnowing: Local Algorithms for Document Fingerprinting." SIGMOD 2003, pp. 76-85. DOI 10.1145/872757.872770.
URL: https://sschleimer.warwick.ac.uk/Maths/winnowing.html
Summary: k-gram winnowing fingerprinting; basis of MOSS (and Dolos).
Differs: baseline citation.

**[prechelt2002jplag]** Lutz Prechelt, Guido Malpohl, Michael Philippsen. "Finding Plagiarisms among a Set of Programs with JPlag." J. Universal Computer Science 8(11):1016-1038, 2002. DOI 10.3217/jucs-008-11-1016.
URL: https://www.jucs.org/jucs_8_11/finding_plagiarisms_among_a/Prechelt_L.html
Summary: token-based Greedy String Tiling; >90% of 77 plagiarisms detected; studies disguise attempts.
Differs: baseline citation.

**[maertens2022dolos]** Rien Maertens, Charlotte Van Petegem, Niko Strijbol, Toon Baeyens, Arne Carla Jacobs, Peter Dawyndt, Bart Mesuere. "Dolos: Language-agnostic plagiarism detection in source code." J. Computer Assisted Learning 38(4):1046-1061, 2022. DOI 10.1111/jcal.12662.
URL: https://dolos.ugent.be
Summary: tree-sitter tokenization + winnowing, language-agnostic, open source.
Differs: baseline citation.

**[maertens2024dolos]** Rien Maertens, Maarten Van Neyghem, Maxiem Geldhof, Charlotte Van Petegem, Niko Strijbol, Peter Dawyndt, Bart Mesuere. "Discovering and exploring cases of educational source code plagiarism with Dolos." SoftwareX, 2024. DOI 10.1016/j.softx.2024.101755. arXiv:2402.10853.
URL: https://arxiv.org/abs/2402.10853
Summary: Dolos 2.x (web UI, API, CLI).
Differs: cite if using Dolos 2.x.

## 4. Learned code models, benchmarks, and robustness

**[guo2022unixcoder]** Daya Guo, Shuai Lu, Nan Duan, Yanlin Wang, Ming Zhou, Jian Yin. "UniXcoder: Unified Cross-Modal Pre-training for Code Representation." ACL 2022, pp. 7212-7225. DOI 10.18653/v1/2022.acl-long.499.
URL: https://aclanthology.org/2022.acl-long.499
Summary: unified encoder/decoder pre-training with AST + comments and contrastive objective; strong on clone detection and zero-shot code-to-code search.
Differs: our backbone; we test its fine-tuned generalization to an unseen transformation family.

**[feng2020codebert]** Zhangyin Feng et al. "CodeBERT: A Pre-Trained Model for Programming and Natural Languages." Findings of EMNLP 2020, pp. 1536-1547. DOI 10.18653/v1/2020.findings-emnlp.139.
URL: https://aclanthology.org/2020.findings-emnlp.139
Summary: bimodal RoBERTa-style pre-training (MLM + RTD).
Differs: background.

**[puri2021codenet]** Ruchir Puri et al. "CodeNet: A Large-Scale AI for Code Dataset for Learning a Diversity of Coding Tasks." NeurIPS 2021 Datasets and Benchmarks. arXiv:2105.12655.
URL: https://arxiv.org/abs/2105.12655
Summary: 14M samples / 55 languages; Python800 and other benchmarks with similarity baselines.
Differs: our data source.

**[lu2021codexglue]** Shuai Lu, Daya Guo, et al. "CodeXGLUE: A Machine Learning Benchmark Dataset for Code Understanding and Generation." NeurIPS 2021 Datasets and Benchmarks. arXiv:2102.04664.
URL: https://arxiv.org/abs/2102.04664
Summary: 14 datasets / 10 tasks incl. clone detection (BigCloneBench, POJ-104).
Differs: standard clone benchmarks are i.i.d.; we construct a family-held-out split.

**[mou2016tbcnn]** Lili Mou, Ge Li, Lu Zhang, Tao Wang, Zhi Jin. "Convolutional Neural Networks over Tree Structures for Programming Language Processing." AAAI 2016, pp. 1287-1293. DOI 10.1609/aaai.v30i1.10139.
URL: https://ojs.aaai.org/index.php/AAAI/article/view/10139
Summary: TBCNN; source of the OJ / POJ-104 program-classification dataset.
Differs: background (POJ-104).

**[svajlenko2014bigclonebench]** Jeffrey Svajlenko, Judith F. Islam, Iman Keivanloo, Chanchal K. Roy, Mohammad Mamun Mia. "Towards a Big Data Curated Benchmark of Inter-project Code Clones." ICSME 2014, pp. 476-480. DOI 10.1109/ICSME.2014.77.
URL: https://dblp.uni-trier.de/rec/conf/icsm/SvajlenkoIKRM14.html
Summary: BigCloneBench, Java Type-1..4 clones.
Differs: background.

**[yefet2020adversarial]** Noam Yefet, Uri Alon, Eran Yahav. "Adversarial Examples for Models of Code." Proc. ACM Program. Lang. 4(OOPSLA), 2020. DOI 10.1145/3428230.
URL: https://arxiv.org/abs/1910.07517
Summary: DAMP gradient-guided variable renaming and dead-code insertion attacks on code2vec/GGNN/GNN-FiLM.
Differs: adversarial (worst-case) perturbations on non-similarity tasks; we use random, non-targeted family shift and a similarity task with token baselines.

**[rabin2021generalizability]** Md Rafiqul Islam Rabin, Nghi D. Q. Bui, Ke Wang, Yijun Yu, Lingxiao Jiang, Mohammad Amin Alipour. "On the generalizability of Neural Program Models with respect to semantic-preserving program transformations." Information and Software Technology 135:106552, 2021. DOI 10.1016/j.infsof.2021.106552.
URL: https://arxiv.org/abs/2008.01566
Summary: code2vec/code2seq/GGNN often flip predictions under renaming, permutation, dead-code, loop/boolean transforms (method-name prediction).
Differs: closest in spirit (non-adversarial semantics-preserving transforms incl. dead code), but no training on some families + testing on another, no similarity task, no token-detector comparison.

**[bielik2020adversarial]** Pavol Bielik, Martin Vechev. "Adversarial Robustness for Code." ICML 2020, PMLR 119:896-907.
URL: https://proceedings.mlr.press/v119/bielik20a.html
Summary: adversarial attacks + robust training for type prediction; adversarial training alone helps little.
Differs: different task; worst-case robustness.

**[henkel2022semantic]** Jordan Henkel, Goutham Ramakrishnan, Zi Wang, Aws Albarghouthi, Somesh Jha, Thomas Reps. "Semantic Robustness of Models of Source Code." SANER 2022, pp. 526-537. DOI 10.1109/SANER53432.2022.00070.
URL: https://arxiv.org/abs/2002.03043
Summary: k-transformation robustness; robust training beats augmentation; robust models better on unseen data sources.
Differs: does not hold out a transformation family; different task. (Note: arXiv lists Ramakrishnan first.)

**[jain2021contracode]** Paras Jain, Ajay Jain, Tianjun Zhang, Pieter Abbeel, Joseph Gonzalez, Ion Stoica. "Contrastive Code Representation Learning." EMNLP 2021, pp. 5954-5971. DOI 10.18653/v1/2021.emnlp-main.482.
URL: https://aclanthology.org/2021.emnlp-main.482
Summary: ContraCode; compiler-based semantics-preserving augmentations (incl. dead-code elimination, renaming) for contrastive pre-training; +39% AUROC on adversarial clone detection vs RoBERTa.
Differs: augmentation families overlap train and test; no token-detector baselines.

**[bui2021corder]** Nghi D. Q. Bui, Yijun Yu, Lingxiao Jiang. "Self-Supervised Contrastive Learning for Code Retrieval and Summarization via Semantic-Preserving Transformations." SIGIR 2021, pp. 511-521. DOI 10.1145/3404835.3462840.
URL: https://arxiv.org/abs/2009.02731
Summary: Corder; contrastive pre-training on renaming, permutation, dead-code insertion, loop exchange variants.
Differs: no held-out-family evaluation; retrieval/summarization tasks.

**[yang2022alert]** Zhou Yang, Jieke Shi, Junda He, David Lo. "Natural Attack for Pre-trained Models of Code." ICSE 2022. DOI 10.1145/3510003.3510146.
URL: https://arxiv.org/abs/2201.08698
Summary: ALERT naturalness-aware renaming attack on CodeBERT/GraphCodeBERT incl. clone detection (POJ/BCB-style); adversarial fine-tuning.
Differs: renaming-only adversarial attack (one of our *training* families); no dead-code held-out test or token baselines.

**[zhang2023clonegen]** Weiwei Zhang, Shengjian Guo, Hongyu Zhang, Yulei Sui, Yinxing Xue, Yun Xu. "Challenging Machine Learning-based Clone Detectors via Semantic-preserving Code Transformations." IEEE TSE, 2023. DOI 10.1109/TSE.2023.3240118. arXiv:2111.10793.
URL: https://arxiv.org/abs/2111.10793
Summary: CloneGen, 15 transformation operators + search (incl. DRL) evade 2 ML and 4 traditional clone detectors; adversarial retraining improves robustness.
Differs: CLOSEST in setup (learned and traditional detectors under SPTs). But: adversarial search, Java/C clone detectors not JPlag/Dolos, no leave-one-family-out, no matched-FPR protocol.

**[sonnekalb2022generalizability]** Tim Sonnekalb, Bernd Gruner, Clemens-Alexander Brust, Patrick Mäder. "Generalizability of Code Clone Detection on CodeBERT." ASE 2022 (Late-Breaking Results). arXiv:2208.12588.
URL: https://arxiv.org/abs/2208.12588
Summary: CodeBERT F1 drops sharply on unseen BigCloneBench functionalities.
Differs: shift over functionalities, not over transformation families.

**[roy2026merging]** Palash R. Roy, Banani Roy, Kevin A. Schneider, Chanchal K. Roy. "A Unified Model for Cross-Domain Clone Detection via Model Merging." ASE 2026. arXiv:2608.04215.
URL: https://arxiv.org/abs/2608.04215
Summary: fine-tuned clone detectors (incl. UniXcoder) collapse out of domain; model merging recovers cross-domain performance.
Differs: domain = dataset/language/AI-generated clones, not transformation family; no token baselines.

**[he2026invpt]** Yifeng He, Yundi Xu, Christopher Castro Gaw Gonzalo, Zili Wang, Hao Chen. "Invariant Pretraining for Robust Code Representations." LMPL 2026 (to appear). arXiv:2608.15412.
URL: https://arxiv.org/abs/2608.15412
Summary: continued pretraining with SPT-augmented MLM + multi-positive contrastive loss; up to +11 pts robustness on clone detection.
Differs: per search-result snippet, the authors caveat that test transforms come from the same operator family used in pretraining (i.e., they explicitly leave unseen-family generalization open), which is the gap we target. Verify in full text before quoting.

**[hooda2025autospt]** Ashish Hooda, Mihai Christodorescu, Chuangang Ren, Aaron Wilson, Kassem Fawaz, Somesh Jha. "Auto-SPT: Automating Semantic Preserving Transformations for Code." arXiv:2512.06042, 2025.
URL: https://arxiv.org/abs/2512.06042
Summary: LLM-synthesized SPT generators; degrade clone detectors; training on them improves robustness.
Differs: no stated held-out-family protocol (abstract); no plagiarism-tool baselines.

## 5. Learned / non-token detectors compared with JPlag/Dolos (novelty-critical)

**[ebrahim2023source]** Fahad Ebrahim, Mike Joy. "Source Code Plagiarism Detection with Pre-Trained Model Embeddings and Automated Machine Learning." RANLP 2023, pp. 301-309.
URL: https://aclanthology.org/2023.ranlp-1.34/
Summary: cosine similarities from pre-trained code model embeddings + AutoML on SOCO; beats JPlag baseline on Java, top on C/C++.
Differs: i.i.d. evaluation on SOCO, no transformation-family split, no matched FPR.

**[ebrahim2026metrics]** Fahad Ebrahim, Mike Joy. "Can Code Evaluation Metrics Detect Code Plagiarism?" LEARNER @ EASE 2026. arXiv:2604.25778.
URL: https://arxiv.org/abs/2604.25778
Summary: CodeBLEU/CrystalBLEU/RUBY/TSED/CodeBERTScore vs JPlag and Dolos on ConPlag and IRPlag across modification levels L1-L6; metrics comparable to tools, degrade from L4.
Differs: untrained metrics, ranking (AUROC) not matched FPR, Java; no held-out family.

**[zubkov2022contrastive]** Maksim Zubkov, Egor Spirin, Egor Bogomolov, Timofey Bryksin. "Evaluation of Contrastive Learning with Various Code Representations for Code Clone Detection." arXiv:2206.08726, 2022.
URL: https://arxiv.org/abs/2206.08726
Summary: SimCLR/SwAV/MoCo x text/AST/graph encoders on POJ-104 and a plagiarism dataset built with CodeTransformator on competitive-programming code; compared with 6 existing approaches incl. traditional tools.
Differs: possibly the closest learned-vs-traditional plagiarism comparison; abstract does not state a held-out transformation family or matched FPR, and it is C++/POJ. Check the full paper before claiming novelty against it.

**[slobodkin2023conplag]** Evgeniy Slobodkin, Alexander Sadovnikov. "Towards a Dataset of Programming Contest Plagiarism in Java." arXiv:2303.10763, 2023.
URL: https://arxiv.org/abs/2303.10763
Summary: ConPlag: 911 manually labeled Codeforces Java pairs (251 plagiarized), evaluated with existing tools.
Differs: real plagiarism, Java; we use synthetic controlled families on Python. Possible external validation set (Java only).
