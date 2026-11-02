# D2 Retraction Watch: lab notebook

## Frozen copy (2026-11-01)
- `git clone --depth 1 https://gitlab.com/crossref/retraction-watch-data` on the VM → `~/d/data/raw/retraction-watch-data/`.
- Repo commit `a98cc7e2dd37b8affab780096048b261833ecc11` (2026-10-30T23:00:11Z); README: "latest dataset … generated on 2026-10-30".
- `retraction_watch.csv` 67,793,090 bytes, UTF-8, sha256 `7a729a87837985954a34326202cb98c4bff4b2b142fda8695febb613cf45a7f4`; 73,519 rows, 20 columns (plus one empty trailing column).
- **Licence (D3):** the repo has no LICENSE file and the README names no licence. Crossref's blog (doi:10.13003/692016) says Crossref metadata is "freely available to reuse without a license" and asks that published work using the Retraction Watch data cite the source. → Cite it; in the dataset release, include only DOIs/PMIDs, dates and reason categories (no titles, authors or notes), and point to the source.

## d02_rw_20261101_01 (2.6 s; T0 = 2024-01-31 provisional)
Script keeps no author, institution, title or notes fields.
- Rows by nature: Retraction 68,077; Expression of concern 3,734; Correction 1,545; Reinstatement 163. All dates parse.
- Retraction rows: with DOI 62,191; with PMID 30,615; with neither 5,172; biomedical subject code (BLS/HSC) 34,776.
- Paper level (key = DOI, else PMID; earliest notice; reasons unioned): **62,735 retracted papers**, 30,601 with a PMID, 1 later reinstated.
- Retracted by T0: 49,544; **after T0: 13,191**.
- Biomedical (PMID or BLS/HSC subject): by T0 28,734; after T0 8,606, of which **5,789 were published 2015–2023** (6,266 for 2010–2023) and **654 of those are paper-mill cases**; 7,212 of the 8,606 have a PMID.
- After-T0 biomedical by notice year: 2024 3,356; 2025 3,658; 2026 (to Oct 30) 1,592.
- Paper-mill papers overall 11,716; by notice year 2020 246, 2021 815, 2022 934, **2023 6,782**, 2024 1,805, 2025 1,115.
- Median lag (notice − publication): 1.51 years for biomedical by T0; 2.68 for after T0.
- Outputs: `reason_counts.csv`, `papers_by_notice_year_mill.csv`; paper table `~/d/data/work/rw_papers_d02_rw_20261101_01.parquet` (sha256 `809945a3…`).
- Note: the biomedical flag here is provisional; D5 defines biomedical by PubMed presence.

## Licence check before the Zenodo deposit (2026-11-01)
Crossref's metadata-retrieval documentation (https://www.crossref.org/documentation/retrieve-metadata/, read 2026-11-01) lists the "Open Funder Registry and Retraction Watch database" as **CC0** in its licence table, and states "We release any Crossref-generated data, including aggregations, as public domain material." The GitLab repository itself still has no LICENSE file; Crossref's blog asks published work to cite the source (a request, not a condition). The deposited dataset takes only factual fields (DOI, PMID, dates, reasons, article type) and no titles, authors, institutions or notes.
