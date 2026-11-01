# D11 RQ4 (citations around retraction): lab notebook

Design: retracted biomedical papers with a first Retraction Watch notice in 2000–2021, a journal, and publication year ≤ notice year; one control per retracted paper from the same journal and publication year (not retracted), drawn with a fixed seed (DuckDB `setseed(0.20261101)`, random order within journal × year). Citations counted by citing publication year relative to the notice year, k = −5 … +2. Descriptive; a replication on open data, not a contribution (see `lit/LIT.md` refs 7, 8).

## d11_event_20261101_01 (53 s)
- Eligible retracted papers 12,197; matched pairs 11,788 (767 paper-mill).
- Citations per paper (control / retracted / ratio):
  | k | control | retracted | ratio |
  |---|---|---|---|
  | −5 | 1.089 | 1.382 | 1.27 |
  | −4 | 1.334 | 1.727 | 1.29 |
  | −3 | 1.614 | 2.095 | 1.30 |
  | −2 | 2.017 | 2.672 | 1.32 |
  | −1 | 2.610 | 3.428 | 1.31 |
  | 0 | 3.515 | 4.252 | 1.21 |
  | +1 | 4.192 | 2.846 | **0.68** |
  | +2 | 4.109 | 1.961 | **0.48** |
- Reading: before retraction, retracted papers are cited about 30% more than journal-and-year matched controls; one and two years after the notice year they receive 0.68 and 0.48 times the controls' citations. Citations continue after retraction (about 2 per paper in year +2).
- Caveat: years after 2023 are not observed; 2023 is partial for both arms. Per-arm, per-mill table: `citations_by_relative_year.csv`.

## d11_event_20261101_02 (cited) and _03 (repeat): reproducibility fix
Reason: `_01` drew controls with DuckDB `setseed` + `random()` (not reproducible under multi-threading). `_02` picks the control with the lowest `hash(iid, 20261101)` within journal × year. **`_03` is an identical repeat: run.json results and `citations_by_relative_year.csv` are byte-identical to `_02`.**
- 11,788 pairs (767 paper-mill), as before. Retracted arm unchanged (same papers); controls differ.
- Ratio retracted / control, k = −5 … +2: 1.30, 1.34, 1.32, 1.32, 1.32, 1.20, **0.66, 0.47** (was 0.68, 0.48).
