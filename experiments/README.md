# Project D experiments: index and where every record lives

| Folder | Step | Runs cited in the paper | Notebook |
|---|---|---|---|
| `d00_setup/` | VM restore, ID map (Meta → DOI/PMID → graph node), effective snapshot date | `d00_idmap_20261101_01`, `d00_cutoff_20261101_01` | `RESULTS_LOG.md` |
| `d02_retraction_watch/` | Frozen Retraction Watch copy; paper-level table; counts | `d02_rw_20261101_01` | `RESULTS_LOG.md` |
| `d04_pubmed/` | PubMed 2026 baseline parser (with grant agencies) and unit test | `d04_pubmed_20261101_01` | `RESULTS_LOG.md` |
| `d05_match/` | Retraction Watch → graph nodes; PubMed cross-check; population sizes | `d05_match_20261101_02` | `RESULTS_LOG.md` |
| `d07_prereg/` | Design specification (frozen; SHA-256 in the notebook) | – | `RESULTS_LOG.md` |
| `d08_rq1/` | Main test: frozen scores, then evaluation | `d08_scores_20261101_01`, `d08_eval_20261101_03` | `RESULTS_LOG.md` |
| `d09_concentration/` | Community concentration vs journal-year matched controls | `d09_conc_20261101_03` | `RESULTS_LOG.md` |
| `d10_nih/` | NIH-funded papers citing retracted work | `d10_nih_20261101_01` | `RESULTS_LOG.md` |
| `d11_event/` | Citations around retraction vs matched controls | `d11_event_20261101_02` (`_03` = repeat, identical) | `RESULTS_LOG.md` |
| `d12_check/` | Label-quality checks (match precision; PubMed-only retractions) | `d12_check_20261101_02` | `RESULTS_LOG.md` |
| `d13_figures/` | Paper figures from run records | `d13_fig_20261101_08` | `RESULTS_LOG.md` |
| `d15_review1/` | **Post hoc** (review round 1): reference-list length (deciles in the MH strata), share version S2, reviews vs research articles | `d15_lenadj_20261101_01`, `d15_screen_20261102_01` | `RESULTS_LOG.md` |
| `d14_dataset/` | Release dataset (built on the VM) and Zenodo draft | `d14_dataset_20261101_04` (`_05` = identical repeat), `d14_zenodo_20261101_01` | `RESULTS_LOG.md` |

Runs not cited (failed, stopped or superseded) are listed with the reason in `../REPRODUCE.md` §5 and carry a
`SUPERSEDED.txt` in their folder.

| Record | Where |
|---|---|
| Lab notebook | `<exp>/RESULTS_LOG.md` |
| Per-run config, script hash, counts | `<exp>/runs/<run_id>/run.json` |
| Per-run checksums | `<exp>/runs/<run_id>/SHA256SUMS` |
| Run stdout | `<exp>/runs/<run_id>/stdout.log` |
| Large intermediates (ID map, PubMed table, frozen scores, matched tables, memberships, release files) | VM disk `~/d/data/work/`, `~/d/data/release/`; archived by snapshot (`../ARCHIVE.md`) |
| Raw inputs | VM `~/d/data/raw/` (Retraction Watch, PubMed) and `~/c/data/raw/` (Data Bank files, Meta dump) |
| VM billing events | `../vm/sessions.log`, `../vm/sessions_notes.log` |

`common.py` is identical in every folder (same SHA-256), so that each folder runs on its own. Scripts refuse to
overwrite an existing run folder.
