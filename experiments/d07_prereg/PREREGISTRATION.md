# D7 pre-registration: does the retracted neighbourhood predict later retraction?

Written 2026-11-01, **before** any score was computed or joined with post-T0 outcomes. What had been seen at that point: label counts and exposure prevalence only (`d05_match_20261101_02`: 4,359 positives among 10,786,018 candidates; 2.0% of candidates cite a paper retracted by T0). No cross-tabulation of exposure and outcome had been run.

This file is frozen once its sha256 is recorded in `RESULTS_LOG.md`. Any later change is an **amendment**: dated, appended at the end, with the reason, and the analyses it affects marked "post hoc" in the paper.

## 1. Data (fixed)
- Graph: OpenCitations Jan 2024 (Data Bank DOI 10.13012/B2IDB-5216575_V1), C's `edges.parquet`, `pubs_slim.parquet`, `pubs_j.parquet` (journal rule `main` of run `c6_full_20261031_02`).
- IDs: `d00_idmap_20261101_01`. PubMed: `d04_pubmed_20261101_01`. Retraction Watch: frozen copy a98cc7e (2026-10-30), `d02_rw_20261101_01`; matching `d05_match_20261101_02` (`status` table: first Retraction Watch retraction notice per iid).
- Label source: Retraction Watch only (nature = Retraction). PubMed flags are a check, not a label.

## 2. Time points
- **Main T0 = 2024-01-31.** R0 = graph nodes with a first retraction notice ≤ T0.
- **Sensitivity T0' = 2023-09-30** (the graph is complete to about Sept 2023; `d00_cutoff_20261101_01`). All of §3–§6 is repeated with T0'.
- Outcome window: (T0, 2026-10-30].
- **Training window** (only for the combined model, §5.3): T−1 = 2021-12-31; outcome window (T−1, T0]; candidates published 2013–2021 and not retracted by T−1; features computed with R(T−1).

## 3. Populations
- **Biomedical node:** has a PMID in Meta, or its DOI is a PubMed DOI (as in d05).
- **Candidates (main):** biomedical, `pub_year` 2015–2023, not in R0, at least one reference in the graph (out-degree ≥ 1), and a journal (`journal_id` from `pubs_j`).
- **Positive:** candidate whose first retraction notice is in the outcome window. Secondary outcome: positive with a Retraction Watch reason containing "Paper Mill".
- Sensitivities: (a) `pub_year` 2015–2022 (complete years); (b) exclude candidates whose DOI maps to more than one iid; (c) T0'.

## 4. Scores (computed by `d08_scores.py` with no access to post-T0 labels)
For candidate *p* with out-degree *d(p)*:
- **S1 = out_r(p):** number of *p*'s references that are in R0. (Primary score.)
- **S2 = out_r(p) / d(p).**
- **S3 = in_r(p):** number of citations *p* received from nodes in R0.
- **S4 = out_r_mill(p):** references to R0 nodes whose Retraction Watch reasons include "Paper Mill".
- **B = journal baseline:** for *p*'s journal *j*, B = (r_j + m·g) / (n_j + m), where n_j = biomedical items in *j* with `pub_year` from 2010 to min(year(T), 2023), r_j = those retracted by T (R0 for the main analysis), g = overall r/n over all journals, m = 100.
- Ties: broken with a fixed random seed 20261101.

## 5. Analyses (all pre-specified)
### 5.1 Association and dose
Positive rate (with 95% Wilson CI) for S1 = 0, 1, 2, 3–4, ≥5; risk ratio of S1 ≥ 1 vs S1 = 0. Same for S3 ≥ 1 and S4 ≥ 1.

### 5.2 Within journal (primary test)
Mantel–Haenszel odds ratio of exposure (S1 ≥ 1) on outcome, stratified by journal × `pub_year`, with the Robins–Breslow–Greenland 95% CI. Strata without both exposed and unexposed, or without any positive, do not contribute (reported). Repeated for S3 ≥ 1, and separately for paper-mill and non-paper-mill outcomes.

**Decision rule (fixed now):** the neighbourhood signal "holds within journal" if the MH OR for S1 ≥ 1 has a 95% CI above 1. If the CI includes 1, the paper reports that the published association (Lou, Zhou & Li 2026) is explained by journal and year in this data.

### 5.3 Screening value
Rank all candidates by: (i) S1 (ties by S2, then seed); (ii) B; (iii) a combined logistic model with features logit(B), log1p(S1), log1p(S3), S1 ≥ 1, and indicators of age at the time point (year(T) − `pub_year`, capped at 8; publication years differ between windows, ages overlap), **fitted only on the training window** (§2) and applied unchanged to the test candidates. Report precision@k and lift (precision / base rate) for k = 100, 1,000, 10,000; recall@10,000; average precision (AUC-PR). 95% CIs by bootstrap over candidates (1,000 resamples, seed 20261101). Primary comparison: combined (iii) vs journal-only (ii) at k = 1,000.

### 5.4 Checks
- Share of positives already flagged in PubMed before T0 (should be 0 by construction; any non-zero is reported as label noise).
- The same tables for exposure prevalence by publication year.

## 6. What will not be reported
No per-paper scores, ranks or lists of unretracted papers, in the paper or the released data. Only aggregates. Retracted papers may be listed by DOI (public labels).

## 7. Amendments
(none yet)
