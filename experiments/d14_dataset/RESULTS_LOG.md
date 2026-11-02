# D14 release dataset: lab notebook

## d14_dataset_20261101_01 (82 s)
Built on the VM at `~/d/data/release/d14_dataset_20261101_01/`; **not deposited** (needs the user's go-ahead) and not copied to the laptop (only its README is, as `runs/.../RELEASE_README.md`).
- `retracted_papers.csv.gz`: 62,735 rows (52,254 in the graph), 1,325,483 bytes, sha256 4d604509…
- `citation_edges.csv.gz`: 2,259,192 citation links touching a retracted paper, 76,057,187 bytes, sha256 5a0e193a…
- `README.md`, `SHA256SUMS`.
- Not included: community IDs (D9 does not save memberships), scores, author names, titles.
- Open: licence compatibility (Retraction Watch terms; CC BY 4.0 proposed), Zenodo deposit.

## d14_dataset_20261101_02 (current release build): reproducibility fix
`citation_edges.csv.gz` is now sorted (citing, cited) so its checksum is reproducible. Same counts: 62,735 retracted papers (52,254 in the graph), 2,259,192 edges. SHA-256: retracted_papers.csv.gz `ac62a7e3…14da`, citation_edges.csv.gz `3fe1d15f…03cc`, README.md `267cf5d4…fc98`. On the VM at `~/d/data/release/d14_dataset_20261101_02/`; not deposited.

## d14_dataset_20261101_03 → _04 (deposited) and _05 (repeat), 2026-11-01
- `_03` adds `communities.csv.gz` (2,698,556 rows: OMID, DOI, PMID, Leiden community for seeds 1 and 2, from `d09_conc_20261101_03`), as the paper's availability text promised. Its `retracted_papers.csv.gz` checksum differed from `_02`: rows with the same date and no DOI, and the OMID list per paper, were not ordered.
- `_04`: rows ordered by (notice date, DOI, PMID, key) and OMID lists sorted. `_05` is a repeat: **all three data files byte-identical to `_04`**.
- `_04` SHA-256: retracted_papers.csv.gz `8b3e9073…a31` (1,325,322 B), citation_edges.csv.gz `3fe1d15f…03cc` (56,414,957 B), communities.csv.gz `c3810b44…78a6b7` (38,319,591 B).

## d14_zenodo_20261101_01: Zenodo DRAFT (not published)
- `d14_zenodo.py` (token from `~/.zenodo_token` on the VM, mode 600; never logged): draft **23874477**, reserved DOI **10.5281/zenodo.23874477**, 5 files uploaded (README.md, the three data files, SHA256SUMS); **MD5 of every file matches Zenodo's**. State: unsubmitted. Metadata: `runs/d14_zenodo_20261101_01/zenodo_metadata.json` (CC BY 4.0, dataset, version 1.0, related identifiers: companion repo, Data Bank DOI, Meta DOI).
- Publishing is done by the user on zenodo.org (irreversible: DOI live, files fixed).

## 2026-11-01: published by the user
Checked via the Zenodo API: record 23874477 status "published", publication date 2026-11-01, open access, CC BY 4.0, 5 files (sizes as uploaded); doi.org/10.5281/zenodo.23874477 resolves. Cited in the paper (Methods, Data availability; `arjomandi2026retracteddata`). The upload token was revoked by the user (requested; confirm).
**When the paper has an arXiv ID or journal DOI:** edit the Zenodo record's metadata (no new version needed) and add it as a related identifier ("is supplement to").

Note 2026-11-01: `d14_dataset.py` and `d14_zenodo.py` templates now state the Retraction Watch licence (CC0 per Crossref). The published v1.0 record was built with the earlier text; its Zenodo description is to be edited by the user (see `paper/Critic/round_1_D_response.md`).

## 2026-11-02 (UTC): Zenodo description edited via API (metadata only)
At the user's request, using the user's token once more (written to a 600-mode temp file, shredded after each call; never logged). Legacy `PUT /api/deposit/depositions/23874477` returned 404 until an edit draft existed; `POST /api/records/23874477/draft` (InvenioRDM) opened it; a full-object `PUT .../draft` returned 500; the legacy `PUT` with legacy metadata fields then succeeded (200) and `actions/publish` returned 202.
Verified unauthenticated on the public API: status published, same DOI 10.5281/zenodo.23874477, version 1.0, CC BY 4.0, same 5 files and sizes, same related identifiers. Description now states Retraction Watch = CC0 per Crossref (permits redistribution), "design specification" (not "pre-registration"), "manuscript in preparation" (not "submitted"). Update to "submitted"/journal reference after submission. The files' README.md still says "submitted" (files are fixed).
