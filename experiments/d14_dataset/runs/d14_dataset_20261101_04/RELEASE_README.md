# Retraction-labelled open citation neighbourhoods (biomedical and other fields), v1

Built 2026-11-02T02:17:01Z by `d14_dataset.py` (run d14_dataset_20261101_04).

## Files
- `retracted_papers.csv.gz` (62,735 rows): every Retraction Watch paper with nature "Retraction" in the copy of
  30 Oct 2026 (repository commit a98cc7e), one row per paper (DOI, else PMID): DOI, PMID, date of the first retraction notice,
  publication year, paper-mill flag (any reason containing "Paper Mill"), Retraction Watch reasons and article type,
  OpenCitations OMIDs of the matched graph node(s), and whether it is in the graph (52,254 are).
- `citation_edges.csv.gz` (2,259,192 rows): every citation in the OpenCitations January 2024 snapshot
  (doi:10.13012/B2IDB-5216575_V1) in which the citing or the cited paper is retracted; both ends with OMID, DOI, PMID and year.

- `communities.csv.gz` (2,698,556 rows): Leiden (modularity, two iterations)
  community of every node in the subgraph used for the concentration analysis (retracted biomedical papers with a journal,
  one non-retracted paper per retracted paper from the same journal and publication year, and all their citation
  neighbours), for seeds 1 and 2 (run d09_conc_20261101_03). Membership in this subgraph says nothing about a paper's status.

## Time split
Retraction dates allow any time point T: papers retracted on or before T are "known"; later ones are outcomes. The graph is
essentially complete to about September 2023.

## What is not included
No author names, titles, abstracts or notes; no scores or rankings of non-retracted papers. A retraction is a public
editorial label and does not imply misconduct.

## Sources and licences
OpenCitations data CC0 / the parsed snapshot CC BY 4.0 (Illinois Data Bank); OpenCitations Meta CC0; Retraction Watch data
from Crossref (cite: Crossref, Retraction Watch database); PubMed identifiers courtesy of the U.S. National Library of Medicine
(may not reflect the latest NLM data). This derived dataset: CC BY 4.0.

## Cite
Please cite the article (Mohasel Arjomandi, *Do links to retracted papers predict future retractions? An out-of-sample
test on the open biomedical citation graph*, submitted) and this dataset. Code and run records:
https://github.com/HosseinMA96/retracted-neighbours-open-data
