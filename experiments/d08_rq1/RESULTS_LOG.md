# D8 RQ1 (prospective test): lab notebook

Pre-registration: `../d07_prereg/PREREGISTRATION.md` (sha256 cf15bfc2…).

## d08_scores_20261101_01 (223 s): scores FROZEN 2026-11-01T15:42:19Z, before any outcome join
- Biomedical nodes 31,464,435; with a journal 30,895,140; iids sharing a DOI with another iid 4,595,629.
- **main_T0** (T0 2024-01-31): R0 44,401 retracted nodes; candidates with journal 10,726,906; scored (≥1 reference) **10,495,850**; S1 ≥ 1: 218,561 (S1 = 1: 187,735; 2: 23,200; 3–4: 6,175; 5+: 1,451); S3 ≥ 1: 172,149; S4 ≥ 1: 28,188; 25,413 journals. g = 0.001234. sha256 `daf059df…f11f1f`.
- **sens_T0p** (2023-09-30): R 38,070; scored 10,499,105; S1 ≥ 1: 206,983. sha256 `c118fbdf…9ca3`.
- **train_Tm1** (2021-12-31, pub 2013–2021): R 24,494; scored 9,903,844; S1 ≥ 1: 153,732. sha256 `16b893ac…6c9a71`.
- Per-paper tables stay on the VM (`~/d/data/work/d08/`); never released.
- `d08_eval.py` written against §5 before this freeze; two fixes made before its first run (no results seen): reproducible bootstrap seeds (crc32 instead of Python's salted `hash`), and removal of an unused slow aggregation.

## d08_eval_20261101_01: STOPPED by me after the training fit (no test result was computed or seen)
sklearn `LogisticRegression(C=1e6, lbfgs)` finished in seconds on 9,903,844 rows (4,638 positives) with intercept −0.125 and coefficients ≈ 0.001 for every neighbourhood feature: the optimizer stopped early (rare outcome, default tolerance), so the fit is not the maximum-likelihood model the pre-registration specifies. Fix: the same model (same features) fitted by Newton's method in statsmodels (`Logit`, tol 1e-10), with an assertion that it converged. Rerun as `_02`. The run folder `_01` has only stdout.

## d08_eval_20261101_02 (1,200 s; 1,000 bootstrap resamples; frozen-score sha256s verified at start)
Training fit (Newton, converged in 14 iterations, 9,903,844 candidates, 4,638 positives in (2021-12-31, 2024-01-31]): logit_b 0.713 (SE 0.011), log1p(S1) 1.110 (0.149), log1p(S3) 2.175 (0.064), S1≥1 0.702 (0.131); age indicators −1.07 to −2.63.

**Main (T0 2024-01-31): 10,495,850 candidates, 4,323 positives (base rate 0.0412%), 418 paper-mill.**
- §5.1 Dose (positive rate, Wilson 95% CI): S1 = 0: 0.0354% [0.0343, 0.0366] (n 10,277,289); 1: 0.267% [0.245, 0.292]; 2: 0.513% [0.429, 0.613]; 3–4: 0.826% [0.629, 1.084]; 5+: 0.758% [0.424, 1.352] (n 1,451).
- Risk ratios: S1 ≥ 1 **8.82** [8.13, 9.57] (683 of 218,561 exposed retracted later); S3 ≥ 1 6.81 [6.17, 7.52]; S4 ≥ 1 (cites a paper-mill retraction) 17.8 [15.5, 20.6].
- **§5.2 primary test, within journal × year (MH OR, RBG CI): S1 ≥ 1 = 2.99 [2.73, 3.27]** (1,201 informative strata, 4,258 positives). Paper-mill outcome 3.37 [2.65, 4.29]; non-mill 2.92 [2.65, 3.21]. S3 ≥ 1: 3.76 [3.37, 4.20] (mill 4.57, non-mill 3.61).
- **Decision rule (pre-registered): CI above 1 → the neighbourhood signal holds within journal.**
- §5.3 Screening (point [95% bootstrap CI]):
  | Ranking | prec@100 | prec@1,000 | prec@10,000 | lift@1,000 | recall@10,000 | AP |
  |---|---|---|---|---|---|---|
  | S1 | 0 | 0.90% [0.40, 1.50] | 0.72% [0.56, 0.89] | 21.9 [9.6, 37.1] | 1.67% | 0.0013 |
  | Journal B | 0 | 0 [0, 0] | 0.02% | 0 | 0.05% | 0.0023 |
  | Combined (trained on earlier window) | 1% | 0.40% [0.10, 0.80] | 0.79% [0.61, 0.94] | 9.7 [2.4, 19.7] | 1.83% | 0.0037 |
  Primary comparison (combined vs journal, k = 1,000): 0.40% vs 0%; combined ranks better, but the S1 count alone does better than the combined model at k = 1,000 (post hoc observation, not a pre-registered test).
- §5.4: of the 4,323 positives, the PubMed retraction notice (via RetractionIn) has publication year 2023 for 1, 2024 for 1,575, 2025 for 1,086, 2026 for 92: label timing is consistent (1 possible pre-T0 notice). Exposure prevalence by publication year 1.9–2.2% (stable).

**Sensitivities**
- (a) pub 2015–2022: MH OR 3.10 [2.82, 3.41]; combined prec@1,000 1.0%, lift 27.3.
- (b) no duplicate-DOI candidates: unchanged (MH OR 2.99 [2.73, 3.27]).
- (c) **T0' = 2023-09-30** (7,578 positives, 3,141 paper-mill): MH OR all 2.00 [1.86, 2.15]; **paper-mill 1.27 [1.13, 1.42]**; non-mill 2.97. Screening flips: **journal B prec@1,000 7.4% [5.6, 9.0], lift 103**; S1 1.1%; combined 2.9%.

**Reading (for the paper; check every claim against these numbers):**
1. The association published by Lou et al. holds prospectively and within journal and year: candidates citing a paper already retracted were about 3 times as likely (odds) to be retracted in the next 2.75 years as papers in the same journal and year that did not.
2. As a screening tool it is weak in absolute terms: about 1 in 110 of the top 1,000 flagged papers was retracted (base rate 1 in 2,400). Most later retractions (3,640 of 4,323, 84%) cite no retracted paper at all.
3. Journal-level retraction waves dominate when they are still running: with T0' (Sept 2023), the late-2023 mass retractions fall in the outcome window and the journal rate becomes the best screen (lift ≈100), and the within-journal paper-mill effect shrinks to 1.27. By Jan 2024 those waves are in the past, and the journal rate no longer ranks future retractions (0 of the top 1,000).
4. Being cited *by* a retracted paper (S3) is at least as informative as citing one (MH 3.76 vs 2.99).

## d08_eval_20261101_03 (cited run): reproducibility fix
Reason: in `_02` the row order after the label join was not fixed, so random tie-breaks and bootstrap weights depended on DuckDB's thread scheduling. `_03` sorts rows by node ID first (`ORDER BY s.iid`); nothing else changed. Frozen score hashes verified again.
- Identical to `_02`: every dose, risk-ratio and Mantel–Haenszel number in all four settings; the training fit (log-likelihood differs in the 16th digit).
- Changed through tie-breaks only: journal-rate ranking, main: prec@1,000 **0.10% [0, 0.30]** (1 positive; was 0), lift 2.4; T0': journal-rate prec@1,000 **6.8% [5.4, 8.4], lift 94** [75, 117] (was 7.4%, 103), prec@100 3% (was 10%). S1 and combined rankings: point values unchanged, CIs move in the third digit.
- The pre-registered decision (MH OR 2.99 [2.73, 3.27] > 1) is unchanged.
