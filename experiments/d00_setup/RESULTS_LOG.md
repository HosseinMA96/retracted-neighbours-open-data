# D0 setup: lab notebook

## 2026-11-01: VM restored from the C snapshot
- The C VM and `rg-project-c` had been deleted (2026-11-01); the disk was archived first as `snap-project-c-osdisk-20261031` (`rg-research-archive`, incremental, 256 GB). The snapshot itself is not modified.
- `vm/vmctl.sh restore`: new group `rg-project-d`, Premium_LRS 256 GB disk from the snapshot, VM `vm-project-d` (Standard_E8s_v6, 8 vCPU, 62 GiB visible, NVMe), SSH from the laptop IP only, auto-shutdown 07:00 UTC (moved to 09:30 for today's runs; see `vm/sessions_notes.log`).
- First reads are slow (74% I/O wait in `top`): a disk created from a snapshot is hydrated lazily.
- Disk after restore: 247 GB, 111 GB used. `~/c/data/raw` 77 GB (Data Bank `_iid_el`/`_pubs` gz, Meta zip + 28,255 extracted CSVs), `~/c/data/work` 27 GB (C's `c6_full_20261031_02`: `edges.parquet` 12.1 GB, `pubs_slim.parquet` 0.85 GB, `meta_venue.parquet`, `pubs_j.parquet`, `pairs_all_years.parquet`).
- Schemas: `edges(citing_iid, cited_iid)`; `pubs_slim(iid, pub_year, type, omid, venue_omid, issns)`.
- **Meta `id` holds `doi:` and `pmid:`** next to the OMID (read from `meta_csv/0.csv`), so no API calls are needed for matching.
- Environment `d` (micromamba, conda-forge): python 3.11, duckdb 1.5, pandas, pyarrow, lxml, python-igraph, leidenalg, scipy. Lock file: TODO (export with `micromamba env export -n d`).

## d00_idmap_20261101_01 (372 s)
Meta CSV → (omid, doi, pmid) long table joined to `pubs_slim` → `~/d/data/work/idmap.parquet` (1.28 GB).
- Meta rows 107,067,700, all with an OMID, all distinct. With DOI 94,599,878 (207,465 with several); with PMID 26,582,951 (57,011 with several).
- Graph nodes (iids) with a PMID: **26,582,951**; with a DOI: **91,379,362**. Pubs rows 107,030,533; 3,474,285 pubs OMIDs are not in Meta v7.
- **Duplicates:** 2,303,785 DOIs map to more than one iid, and 20,727 PMIDs do. Matching must take the union of iids per paper and report it.
- PMID nodes by publication decade: 2000s 5,525,907; 2010s 9,507,062; 2020s 3,848,034.

## d00_cutoff_20261101_01 (342 s): effective snapshot date
Meta records by `pub_date` month: about 240k–300k per month Jan–Sep 2023, then **58,434 (Oct), 35,739 (Nov), 25,699 (Dec), 6,223 (Jan 2024)**. Citing edges by citing month: about 8.7M–10.3M per month Jan–Sep 2023, then 2.4M (Oct), 1.6M (Nov), 1.1M (Dec), 0.28M (Jan 2024).
- **Reading:** the graph is effectively complete up to about **September 2023**; later months are partial. TODO(verify) the nominal dump date in the Data Bank README (the page returns 403 to scripted fetches; check in a browser).
- **Consequence for the design (to fix in the D7 pre-registration):** no post-T0 information is in the graph, so T0 = 2024-01-31 (retractions known by then) is leak-free. Proposed: main T0 = 2024-01-31, sensitivity T0 = 2023-09-30 (graph and labels aligned). Papers published Oct 2023 – Jan 2024 have incomplete references; the candidate window should end at 2023-09 or report it.
