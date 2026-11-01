# Project D literature (D1 gate, 2026-11-01)

Every DOI below was resolved through the Crossref or DataCite API on 2026-11-01 (title, venue, year and first authors matched). "Read" says how much was read: **abstract** (Crossref/DataCite abstract or publisher page), **full** (full text), or **snippet** (search summary only; must be read before citing a specific claim). Nothing marked *snippet* may be cited for a specific finding.

## Closest prior work

| # | Reference | DOI | Read | What it does | Overlap with D |
|---|---|---|---|---|---|
| 1 | Lou, Zhou & Li (2026), *Beyond Retractions: A Topic-Based Analysis of the Impact and Lifespan of Retracted Papers*, J. Data and Information Science | 10.1515/jdis-2026-0064 | abstract | >50,000 WoS retractions; citation impact and lifespan; "retractions are not randomly scattered but tend to cluster within citation networks"; "articles citing retracted works are associated with substantially higher subsequent retraction rates", stronger with more retracted references. States: observational, associations only, WoS only | **Highest.** Establishes the association behind RQ1 and the clustering behind RQ2. D must be positioned as a *prospective test* of their association |
| 2 | Feng, Feng, Han & Zhang (2024), *Citation network analysis of retractions in molecular biology field*, Scientometrics 129:4795–4817 | 10.1007/s11192-024-05101-4 | snippet | Retraction Watch + WoS; community detection on the retraction citation network in molecular biology; very high self-citation in the largest communities; reasons | RQ2 (one field) |
| 3 | Candal-Pedreira, Guerra-Tort, Ruano-Ravina et al. (2024), *Retracted papers originating from paper mills: a cross-sectional analysis of references and citations*, J Clin Epidemiol | 10.1016/j.jclinepi.2024.111397 | snippet | 416 paper-mill retractions from 2022; interlinked clusters of retracted papers; suggests the links could flag fraud | RQ1/RQ2 (paper mills, one year) |
| 4 | Candal-Pedreira, Ross, Ruano-Ravina et al. (2022), *Retracted papers originating from paper mills: cross sectional study*, BMJ | 10.1136/bmj-2022-071517 | not yet | Paper-mill retraction characteristics | Background |
| 5 | Cabanac, Labbé et al. (2022), *The 'Problematic Paper Screener' automatically selects suspect publications for post-publication (re)assessment*, arXiv | 10.48550/arXiv.2210.04895 (DataCite) | snippet | PPS incl. the "Feet of Clay" detector (papers citing retracted work); flags used by publishers | The deployed tool whose signal D tests |
| 6 | Fletcher & Stevenson (2025), *Predicting retracted research: a dataset and machine learning approaches*, Res Integr Peer Rev 10:9 | 10.1186/s41073-025-00168-w | full (PMC12153192, via fetch summary) | Retraction prediction from title/abstract + metadata; 9,028 balanced articles 2000–2020; random (not temporal) split; accuracy ≈0.61–0.68; **no citation-network or retracted-reference features** (listed as future work) | Shows the prediction gap D fills; baseline numbers for context |
| 7 | Hsiao & Schneider (2021), *Continued use of retracted papers…in biomedicine*, QSS 2(4):1144 | 10.1162/qss_a_00155 | abstract | 7,813 retracted PubMed papers; iCite citations; PMC citation contexts | RQ4 (post-retraction citation): covered |
| 8 | Joseph (2026), *SaneCite retraction census: post-retraction citations to 22,553 retracted biomedical papers*, Zenodo, CC BY 4.0, v1.3.0 | 10.5281/zenodo.23766253 (DataCite) | abstract | Every RW retraction with a PMID retracted 1990–2023; 55,676 later citations; LLM-labelled citation contexts | RQ4 and the dataset angle: post-retraction citation data now exists. D's dataset must be different (see gap) |
| 9 | van der Vet & Nijveen (2016), *Propagation of errors in citation networks…*, Res Integr Peer Rev | 10.1186/s41073-016-0008-5 | abstract | Full citation network of one retracted Nature paper; direct citations propagate, indirect ones did not | Background for 1-hop vs 2-hop |
| 10 | Memon, West & O'Connor (2025), *Are Widely Known Findings Easier to Retract?*, arXiv | 10.48550/arXiv.2504.15504 (DataCite) | snippet | Citation drop after retraction vs prior attention | RQ4 background |
| 11 | *Quantifying the Dynamics of Harm Caused by Retracted Research* (2025), arXiv | 10.48550/arXiv.2501.00473 (DataCite) | snippet | Harm by citation distance from retracted papers (Semantic Scholar) | 2-hop background; authors TODO |
| 12 | Schneider, Ye, Hill et al. (2020), *Continued post-retraction citation of a fraudulent clinical trial report…*, Scientometrics | 10.1007/s11192-020-03631-1 | snippet | Case study | RQ4 background |
| 13 | Teixeira da Silva et al. (2025), *The Citation of Retracted Papers and Impact on the Integrity of the Scientific Biomedical Literature*, Learned Publishing | 10.1002/leap.1667 | not yet | Review | Background |
| 14 | Peng, Romero & Horvát (2022), *Dynamics of cross-platform attention to retracted papers*, PNAS | 10.1073/pnas.2119086119 | not yet | Attention to retracted papers | Background |

## NIH angle (RQ3)

| # | Reference | DOI | Read | Notes |
|---|---|---|---|---|
| 15 | Stern, Casadevall, Steen & Fang (2014), *Financial costs and personal consequences of research misconduct resulting in retracted publications*, eLife | 10.7554/eLife.02956 | snippet | NIH funding *of retracted papers* (costs), not of citing papers |
| 16 | Azoulay, Furman, Krieger & Murray (2015), *Retractions*, Review of Economics and Statistics | 10.1162/REST_a_00469 | snippet | Retractions followed by lower NIH funding and citations in the related field (PubMed related-articles) |

No study found (2026-11-01 searches) that measures **NIH-funded citing papers** that cite retracted work after retraction. Treat RQ3 as open, but it is descriptive.

## Data sources (for the Data section)

| Reference | DOI | Notes |
|---|---|---|
| Mohasel Arjomandi, Korobskiy & Chacko (2024), *Parsed Open Citations and PubMed Data*, Illinois Data Bank | 10.13012/B2IDB-5216575_V1 (DataCite) | The citation graph (Jan 2024) |
| Massari et al. (2024), *OpenCitations Meta*, QSS | 10.1162/qss_a_00292 | ID map (DOI, PMID) and journals |
| Peroni & Shotton (2020), QSS | 10.1162/qss_a_00023 | OpenCitations |
| Heibi, Peroni & Shotton (2019), *COCI*, Scientometrics | 10.1007/s11192-019-03217-6 | Index |
| Rittman (2025), *Retraction Watch retractions now in the Crossref API*, Crossref blog | 10.13003/692016 | Crossref asks published work to cite the source; no licence named for the data. TODO(verify) the preferred citation for the dataset itself |

## Gate decision (2026-11-01)

**The association is published (ref 1); a prospective test of it is not.** D goes ahead with the reframe, positioned as a test of a published association and a deployed screening signal (refs 1, 3, 5), as C was a test of CIDRE:

1. **Prospective, out of sample.** Ref 1 is retrospective and observational on WoS. D freezes scores on the Jan 2024 snapshot and evaluates against retractions issued Feb 2024 – Oct 2026 (5,789 biomedical papers published 2015–2023; run `d02_rw_20261101_01`).
2. **Beyond the journal.** Retractions cluster in journals (paper mills, special issues). D asks whether the neighbourhood signal adds anything *within journal and year*, which none of refs 1–6 report (TODO(verify) in the full text of ref 1).
3. **Screening value.** Precision@k and lift over a journal-rate baseline, i.e. what a publisher using a Feet-of-Clay-style flag would get. Ref 6 reached accuracy ≈0.61–0.68 without network features.
4. **Open and reproducible.** All inputs are open (OpenCitations, Meta, PubMed, Retraction Watch); refs 1–3 use WoS.
5. **Directions and reasons.** Citing vs cited-by retracted papers; paper-mill vs other reasons.
6. **NIH exposure** (RQ3): no prior measurement found.
7. **Dataset.** Post-retraction citation data now exists (refs 7, 8), so D's release is a **time-split benchmark**: the open citation subgraph around retracted papers with T0 labels and post-T0 outcome labels, so that others can test retraction early-warning methods out of sample. No per-paper risk scores.

**Must read in full before writing:** ref 1 (method: how "subsequent retraction rate" was computed, any controls, any time split), refs 2, 3, 5.
