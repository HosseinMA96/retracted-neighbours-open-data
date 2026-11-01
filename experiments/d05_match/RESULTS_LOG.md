# D5 matching: lab notebook

Labels, coverage and population sizes only. **No scores were computed and exposure was not cross-tabulated with post-T0 outcomes** (that waits for the D7 pre-registration). T0 = 2024-01-31.

## d05_match_20261101_01: FAILED (kept for the record)
Two bugs: `matched` is a reserved word in DuckDB (parser error at the by-period query), and Retraction Watch PMIDs were floats, so `CAST(pmid AS VARCHAR)` gave `12345.0` and PMID matching found 0. The counts logged before the crash (PubMed cross-check, DOI matching) do not depend on either bug and equal those of `_02`. No run.json was written.

## d05_match_20261101_02 (150 s)
Fix: alias `n_matched`; PMIDs cast to BIGINT before VARCHAR. Inputs: `rw_papers_d02_rw_20261101_01`, `idmap.parquet` (d00_idmap), `pubmed26.parquet` (d04), C's `edges.parquet` and `pubs_slim.parquet`.

**Retraction Watch ↔ PubMed**
- 62,735 retracted papers; PMID given 30,601; 314 more PMIDs filled through the PubMed DOI; 83 given PMIDs are not in the 2026 baseline.
- PubMed flags 30,697 papers as retracted (30,695 with both the publication type and RetractionIn; 2 with the type only).
- Of 30,915 Retraction Watch papers with a PMID, **27,456 (88.8%) are flagged in PubMed**. By notice year the share is 81–99% for 2015–2025 and 118/1,369 for 2026 (the baseline predates most 2026 notices).
- 3,205 PubMed-flagged papers are not in Retraction Watch (by PMID or DOI). To inspect in D12; candidate extra labels, reported separately.

**Retraction Watch → graph**
- Matched by DOI 51,673; by PMID 25,208; **either 52,254 of 62,735 (83.3%)**. 893 papers map to several iids (Meta duplicates; their union is used); 19 iids are shared by several Retraction Watch papers.
- By period: retracted by T0 43,528 of 49,544 matched (87.9%); after T0 8,726 of 13,191 (66.2%; many after-T0 retractions were published after the snapshot).
- Retracted nodes 53,170: 3,333 have no references in the graph (out-degree 0), 12,627 have no incoming citations, 292 are isolated. Edges: 1,481,454 out, 799,317 in.

**Populations**
- Biomedical nodes (PMID in Meta, or DOI in PubMed): **31,464,435** (26,582,951 through a Meta PMID).
- Candidates (biomedical, published 2010–2023, not retracted by T0): 15,216,941; **2015–2023: 10,786,018**, of which 10,519,522 have at least one reference in the graph. By year 2015–2023 between 1.02M and 1.48M; 2023 lower (1,046,424; snapshot ends about Sept 2023).
- **Positives** (candidate 2015–2023 retracted after T0): **4,359**; 4,325 with references; **422 paper-mill**. Base rate ≈ 0.040%.
- Exposure prevalence (no outcome involved): 218,844 candidates (2.0%) cite at least one paper retracted by T0; 176,384 are cited by at least one.
- Saved on the VM: `rw2_*`, `rw_iid_*`, `rdeg_*`, `status_*` parquet tables in `~/d/data/work/`.

**Implications for D7**
- 4,359 positives at a 0.04% base rate: precision@k and lift are the right metrics; AUC alone would mislead.
- The 2023 candidate year is partial; decide in the pre-registration whether to cut candidates at publication month ≤ 2023-09.
- 11.2% of Retraction Watch papers with a PMID (3,459 of 30,915) are not flagged in PubMed; keep Retraction Watch as the label source and PubMed as a check.
