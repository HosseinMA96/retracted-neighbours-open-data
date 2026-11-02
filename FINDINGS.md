# Project D findings: every claim → number → run

Write the paper only from this file. Runs cited are the final, deterministic runs (see `REPRODUCE.md`). Each number links to the run whose `run.json` holds it (`experiments/<exp>/runs/<run_id>/`). Large per-paper tables live only on the VM disk (see `ARCHIVE.md` once written).

## Data
| Claim | Number | Run |
|---|---|---|
| Citation graph edges | 1,962,840,983 | C `c6_full_20261031_02` |
| Graph is effectively complete to about Sept 2023 | Meta records ~240–300k/month Jan–Sep 2023, 58,434 in Oct; citing edges ~9.4M/month → 2.4M | `d00_cutoff_20261101_01` |
| Graph nodes with a PMID / DOI | 26,582,951 / 91,379,362 | `d00_idmap_20261101_01` |
| Retraction Watch copy | commit a98cc7e (2026-10-30), CSV sha256 7a729a87…, 73,519 rows | `d02_rw_20261101_01` |
| Retracted papers (paper level) | 62,735 (30,601 with PMID); by T0 49,544; after T0 13,191 | `d02_rw_20261101_01` |
| Paper-mill retractions | 11,716; by first notice year 246 (2020) → 6,782 (2023) | `d02_rw_20261101_01` |
| Retracted papers by first notice year, 2023 (the maximum) | 13,210 | `d02_rw_20261101_01` (`retractions_by_notice_year`) |
| PubMed 2026 baseline | 39,994,988 PMIDs; 30,697 flagged retracted; 3,341,220 with an NIH agency | `d04_pubmed_20261101_01` |
| Retraction Watch papers with a PMID also flagged in PubMed | 27,456 / 30,915 (88.8%) | `d05_match_20261101_02` |
| PubMed-flagged papers missing from Retraction Watch | 3,205 | `d05_match_20261101_02` |
| Retracted papers matched to graph nodes | 52,254 / 62,735 (83.3%); by T0 87.9%, after T0 66.2% | `d05_match_20261101_02` |
| Biomedical graph nodes | 31,464,435 | `d05_match_20261101_02` |

## RQ1: prospective test (pre-specified, `experiments/d07_prereg/PREREGISTRATION.md`, sha256 cf15bfc2…; not a formal registry pre-registration)
| Claim | Number | Run |
|---|---|---|
| Test candidates (biomedical, pub 2015–2023, journal, ≥1 reference, not retracted by 2024-01-31) | 10,495,850 | `d08_scores_20261101_01` |
| Retracted by T0 (graph nodes) | 44,401 | `d08_scores_20261101_01` |
| Candidates citing ≥1 paper retracted by T0 | 218,561 (2.08%) | `d08_scores_20261101_01` |
| Positives (retracted 2024-02-01 to 2026-10-30) | 4,323 (base rate 0.0412%); 418 paper-mill | `d08_eval_20261101_03` |
| Dose: positive rate by S1 = 0/1/2/3–4/5+ | 0.035% / 0.267% / 0.513% / 0.826% / 0.758% | `d08_eval_20261101_03` |
| Risk ratio, S1 ≥ 1 | 8.82 [8.13, 9.57] | `d08_eval_20261101_03` |
| Risk ratio, cites a paper-mill retraction | 17.8 [15.5, 20.6] | `d08_eval_20261101_03` |
| **Primary: within journal × year MH OR, S1 ≥ 1** | **2.99 [2.73, 3.27]**; decision: holds | `d08_eval_20261101_03` |
| Within journal, paper-mill / non-mill outcomes | 3.37 [2.65, 4.29] / 2.92 [2.65, 3.21] | `d08_eval_20261101_03` |
| Within journal, cited by a retracted paper (S3 ≥ 1) | 3.76 [3.37, 4.20] | `d08_eval_20261101_03` |
| Share of positives with no retracted reference | 3,640 / 4,323 (84.2%) | `d08_eval_20261101_03` (dose row S1 = 0) |
| Screening, S1 ranking | prec@1,000 0.90% [0.40, 1.50]; lift 21.9; recall@10,000 1.67% | `d08_eval_20261101_03` |
| Screening, journal-rate ranking | prec@1,000 0.10% [0, 0.30] (1 positive); AP 0.0023 | `d08_eval_20261101_03` |
| Screening, combined model (trained on 2022–Jan 2024 outcomes) | prec@1,000 0.40%; prec@10,000 0.79%; AP 0.0037 | `d08_eval_20261101_03` |
| Sensitivity pub 2015–2022 | MH OR 3.10 [2.82, 3.41] | `d08_eval_20261101_03` |
| Sensitivity no duplicate-DOI nodes | MH OR 2.99 [2.73, 3.27] | `d08_eval_20261101_03` |
| Sensitivity T0' = 2023-09-30 | MH OR 2.00 [1.86, 2.15]; paper-mill 1.27 [1.13, 1.42]; journal-rate prec@1,000 6.8% [5.4, 8.4], lift 94 | `d08_eval_20261101_03` |

## RQ3: NIH exposure (descriptive)
| Claim | Number | Run |
|---|---|---|
| Biomedical papers 2000–2023 / NIH-funded | 21,463,892 / 2,332,727 | `d10_nih_20261101_01` |
| Papers citing a paper after its retraction year: NIH vs non-NIH | 10,872 (0.466%) vs 92,477 (0.484%) | `d10_nih_20261101_01` |
| Within journal × year OR (NIH vs not) | 1.027 [1.004, 1.050] | `d10_nih_20261101_01` |
| Retracted papers cited after retraction by NIH-funded papers | 3,548 (of 13,138 cited after retraction at all) | `d10_nih_20261101_01` |

## RQ4: citations around retraction (descriptive replication)
| Claim | Number | Run |
|---|---|---|
| Matched pairs (notice 2000–2021) | 11,788 | `d11_event_20261101_02` |
| Ratio retracted / control citations per paper, k = −5 … −1 | 1.30–1.34 | `d11_event_20261101_02` |
| Ratio at k = +1 / +2 | 0.66 / 0.47 | `d11_event_20261101_02` |

## RQ2: concentration in communities (descriptive)
| Claim | Number | Run |
|---|---|---|
| Journal-year matched pairs / paper-mill pairs | 27,567 / 5,394 | `d09_conc_20261101_03` |
| Subgraph | 2,698,556 nodes, 57,223,086 edges | `d09_conc_20261101_03` |
| Leiden communities (seed 1 / 2); modularity | 197 / 200; 0.651 / 0.657 | `d09_conc_20261101_03` |
| Seed agreement | ARI 0.41, NMI 0.57 | `d09_conc_20261101_03` |
| Concentration ratio retracted / controls, all | 1.15 / 1.11 (both p = 0.001, null ≈ 1.00) | `d09_conc_20261101_03` |
| Paper-mill | 1.68 / 1.52 (p = 0.001) | `d09_conc_20261101_03` |
| Other retractions | 1.06 / 1.05 (p = 0.001 / 0.001) | `d09_conc_20261101_03` |

## Not claims (do not write)
- Per-paper scores or names of unretracted papers.
- "Fraud" or "misconduct" for any paper: only "retracted" and "cites a retracted paper".
- Causation: all results are associations.

## Added
| Citing links dated after Jan 2024 | 66,100 + 39,206 + 6,505 + 2,622 + 656 + 303 + 731 = 116,123 (0.006% of 1,962,840,983) | `d00_cutoff_20261101_01` |
| Biomedical papers 2000–2023 citing a paper after its retraction year (NIH + non-NIH) | 10,872 + 92,477 = 103,349 | `d10_nih_20261101_01` |
| Median publication-to-retraction lag, biomedical papers retracted after T0 | 2.68 years | `d02_rw_20261101_01` |
| Match precision (hand-read sample) | 0 wrong of 292 judgeable (rule-of-three 95% upper bound ≈1%) | `d12_check_20261101_02` |
| PubMed-flagged, not in Retraction Watch: notices 2024–2026 | 2,365 of 3,205 (74%) | `d12_check_20261101_02` |

## Dataset (Zenodo)
| Claim | Number | Run |
|---|---|---|
| Retracted papers / in the graph | 62,735 / 52,254 | `d14_dataset_20261101_04` |
| Citation links touching a retracted paper | 2,259,192 | `d14_dataset_20261101_04` |
| Community memberships (D9 subgraph) | 2,698,556 | `d14_dataset_20261101_04` |
| Zenodo record | 23874477, DOI 10.5281/zenodo.23874477, **published 2026-11-01** (open, CC BY 4.0) | `d14_zenodo_20261101_01` |

## Post hoc (review round 1): reference-list length and reviews
| Claim | Number | Run |
|---|---|---|
| Median references, candidates citing a retracted paper vs not | 51 vs 34 | `d15_lenadj_20261101_01` |
| MH OR S1 ≥ 1, strata journal × year × reference-count decile | 3.03 [2.76, 3.33] (1,838 strata); paper-mill 4.12 [3.21, 5.29]; other 2.89 [2.61, 3.19] | `d15_lenadj_20261101_01` |
| Same, T0' | 2.47 [2.28, 2.67]; paper-mill 1.92; other 2.94 | `d15_lenadj_20261101_01` |
| MH OR by share S2 vs S2 = 0 (same strata): ≤1% / 1–2% / 2–5% / >5% | 1.74 [1.14, 2.66] / 2.82 [2.33, 3.41] / 2.98 [2.64, 3.35] / 3.96 [3.24, 4.85] | `d15_lenadj_20261101_01` |
| Review share (Review, Systematic Review, Meta-Analysis) by S1 = 0 / 3–4 / 5+ | 11.6% / 47.8% / 69.6% | `d15_lenadj_20261101_01` |
| Reviews with S1 5+ retracted later | 1 of 1,010 (0.10%) | `d15_lenadj_20261101_01` |
| Non-reviews retracted later by S1 = 0 / 1 / 2 / 3–4 / 5+ | 0.036% / 0.35% / 0.79% / 1.52% / 2.27% (10 of 441) | `d15_lenadj_20261101_01` |
| MH OR without reviews (journal × year × decile) | 3.19 [2.90, 3.51] | `d15_lenadj_20261101_01` |
| Lou et al. 2026 (literature, for the contrast) | 9.58% at five retracted references; 1.43% overall vs 0.12% global | `lit/LIT.md` |
