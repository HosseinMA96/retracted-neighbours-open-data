# Reproducing Paper D

Every number in the paper comes from a run listed below; `FINDINGS.md` maps each claim to its run. Each run folder
(`experiments/<exp>/runs/<run_id>/`) holds `run.json` (parameters, SHA-256 of the script, input paths, counts,
runtime), `stdout.log`, small outputs and `SHA256SUMS`. Scripts refuse to write into an existing run folder, so a
rerun always gets a new run ID.

## 1. Machine and environment
- Steps that read the full citation graph need about 64 GB RAM and 150 GB of disk. They were run on one Azure
  `Standard_E8s_v6` VM (8 vCPU, 64 GB, Ubuntu 24.04). Total compute for all runs: a few VM-hours.
- Python environment: `vm/environment_d.lock.yml` (micromamba/conda-forge; Python 3.11, DuckDB 1.5, pandas, pyarrow,
  lxml, python-igraph, leidenalg, scipy, scikit-learn, statsmodels). Create it with
  `micromamba create -n d -f vm/environment_d.lock.yml`.
- VM control: `vm/vmctl.sh` (`restore` builds the VM from a disk snapshot; `start`, `stop` = deallocate, `ssh`,
  `push` copies the code to `~/d`, `fetch RUN` copies a run back and checks its checksums).
- `experiments/<exp>/common.py` is the same file in every folder (identical SHA-256) so that each folder runs on its
  own. Paths default to `~/d/data` (`D_DATA`) and to the folder holding the graph tables (`C_WORK`).

## 2. Inputs
| Input | Source | Check |
|---|---|---|
| Citation graph, January 2024 | Illinois Data Bank, doi:10.13012/B2IDB-5216575_V1: `open_citations_jan2024_iid_el.csv.gz` (14,309,784,846 B), `open_citations_jan2024_pubs.csv.gz` (9,064,662,339 B) | sizes and SHA-256 in `experiments/c01_journal_graph/RESULTS_LOG.md` of https://github.com/HosseinMA96/citation-stacking-open-data |
| Graph tables (`edges.parquet`, `pubs_slim.parquet`, `pubs_j.parquet`) | Built from the two files and the Meta dump by `c6_full_run.py` (run `c6_full_20261031_02`) in the companion repository of the earlier study, https://github.com/HosseinMA96/citation-stacking-open-data | `run.json` of that run there |
| OpenCitations Meta CSV dump | figshare doi:10.6084/m9.figshare.21747461.v7, `meta_csv_dump.zip` | SHA-256 `924ac7acc838024bdc78982970c7b1a4bcd4da5f8ad62c47a94d9580df10ca44` |
| Retraction Watch | `git clone https://gitlab.com/crossref/retraction-watch-data`, commit `a98cc7e2dd37b8affab780096048b261833ecc11` (2026-10-30) | `retraction_watch.csv` SHA-256 `7a729a87837985954a34326202cb98c4bff4b2b142fda8695febb613cf45a7f4` |
| PubMed 2026 baseline | `vm/download_pubmed.sh` (NLM, files pubmed26n0001–1334) | every file checked against NLM's `.md5` |

Place them as: `~/c/data/raw/meta_csv/*.csv`, `~/c/data/work/c6_full_20261031_02/*.parquet`,
`~/d/data/raw/retraction-watch-data/`, `~/d/data/raw/pubmed26/`. The Retraction Watch repository moves daily;
check out the commit above.

## 3. Runs, in order (the runs cited in the paper)
Run each from its experiment folder: `python <script> <run_id> [args]`.

| Step | Command | Time on the VM |
|---|---|---|
| ID map | `d00_setup/d00_idmap.py d00_idmap_20261101_01` | 6 min |
| Snapshot cutoff | `d00_setup/d00_cutoff.py d00_cutoff_20261101_01` | 6 min |
| Retraction Watch | `d02_retraction_watch/d02_rw_counts.py d02_rw_20261101_01` | seconds |
| PubMed parse | `d04_pubmed/test_pubmed_parse.py` (unit test), then `d04_pubmed/d04_run.py d04_pubmed_20261101_01 7` | 33 min |
| Matching | `d05_match/d05_match.py d05_match_20261101_02 d02_rw_20261101_01` | 3 min |
| Pre-registration | `d07_prereg/PREREGISTRATION.md` (SHA-256 `cf15bfc25e66d951bcbf8b1d02a5cb4f8b487be036c05ba400538201087d19ee`, frozen before any score) | – |
| Scores (frozen) | `d08_rq1/d08_scores.py d08_scores_20261101_01 d05_match_20261101_02` | 4 min |
| Evaluation | `d08_rq1/d08_eval.py d08_eval_20261101_03 d08_scores_20261101_01 d05_match_20261101_02 1000` (checks the frozen score hashes first) | 20 min |
| Communities | `d09_concentration/d09_concentration.py d09_conc_20261101_03 d05_match_20261101_02` | 10 min |
| NIH exposure | `d10_nih/d10_nih.py d10_nih_20261101_01 d05_match_20261101_02` | 1 min |
| Event study | `d11_event/d11_event.py d11_event_20261101_02 d05_match_20261101_02` (repeat `_03` = identical) | 1 min |
| Label checks | `d12_check/d12_check.py d12_check_20261101_02 d05_match_20261101_02` | 5 min |
| Figures | `d13_figures/d13_figures.py d13_fig_20261101_08` (reads run records only; runs on a laptop) | seconds |
| Release dataset | `d14_dataset/d14_dataset.py d14_dataset_20261101_04 d05_match_20261101_02 d09_conc_20261101_03` (then `d14_zenodo.py`, deposited as doi:10.5281/zenodo.23874477) | 3 min |
| Paper | `cd paper && tectonic -X compile main.tex` | – |

## 4. Determinism
- All random choices use fixed seeds: control selection by `hash(iid, 20261101)` in DuckDB; tie-breaks and bootstrap
  with NumPy `SeedSequence` from 20261101 after sorting rows by node ID; Leiden seeds 1 and 2 on an edge list sorted by
  node ID; the D12 sample with `random_state=20261101`.
- Floating-point sums in parallel DuckDB aggregations can differ in the last digits between runs.
- Verified: `d11_event_20261101_02` and `_03` are byte-identical.
- Runs made before these fixes (listed below) are kept for the record. The pre-registered associations of D8 did not
  change; screening metrics changed only through tie-breaks; D9 and D11 changed slightly because other controls were
  drawn (details in each `RESULTS_LOG.md`). The paper cites only the runs in §3.

## 5. Runs not cited (kept for the record)
| Run | Why |
|---|---|
| `d05_match_20261101_01` | Failed (SQL keyword; float PMIDs); fixed in `_02` |
| `d08_eval_20261101_01` | Stopped: logistic fit did not converge (L-BFGS); refit with Newton in `_02` |
| `d08_eval_20261101_02` | Superseded by `_03` (row order fixed before tie-breaks and bootstrap) |
| `d09_conc_20261101_01` | Stopped: Leiden to convergence too slow; `n_iterations = 2` in `_02` |
| `d09_conc_20261101_02` | Superseded by `_03` (deterministic controls and edge order) |
| `d11_event_20261101_01` | Superseded by `_02` (deterministic controls) |
| `d12_check_20261101_01` | Superseded by `_02` (deterministic sample order) |
| `d14_dataset_20261101_01`–`_03`, `_05` | Superseded by `_04` (sorted edges; communities added; deterministic row and OMID order); `_05` is an identical repeat |
| `d13_fig_20261101_01`–`_07` | Layout iterations, pre-fix inputs, PDF timestamps; the figures in the paper are `d13_fig_20261101_08` |

## 6. Restoring the large data
The large intermediate tables (ID map, PubMed table, frozen scores, matched tables, community memberships, release
dataset) were kept on the VM disk; at the end of the project that disk is archived as an Azure snapshot. See
`ARCHIVE.md` for the snapshot name, contents and restore steps.
