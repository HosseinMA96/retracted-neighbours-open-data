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
