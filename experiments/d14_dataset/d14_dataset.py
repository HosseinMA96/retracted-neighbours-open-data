"""D14: build the release dataset on the VM (~/d/data/release/<run_id>/). Deposit only after the user's go-ahead.
Files (gzip CSV): retracted_papers (public labels), citation_edges (1-hop links touching a retracted paper, as DOIs/OMIDs),
communities (Leiden memberships of the D9 subgraph, two seeds; optional),
README, LICENSE note, SHA256SUMS. No author names, titles, or any score for non-retracted papers.
usage: python d14_dataset.py RUN_ID MATCH_RUN_ID [COMMUNITY_RUN_ID]
"""
import sys, duckdb, numpy as np, pandas as pd
from common import Run, C_WORK, D_DATA, sha256

W = D_DATA / "work"; M = sys.argv[2]
COMM = sys.argv[3] if len(sys.argv) > 3 else None
run = Run(sys.argv[1], __file__, {"match_run": M, "community_run": COMM})
rel = D_DATA / "release" / sys.argv[1]; rel.mkdir(parents=True)
con = duckdb.connect(); con.execute(f"SET threads=8; SET memory_limit='40GB'; SET temp_directory='{W / 'tmp'}'")
q = lambda s: con.execute(s).fetchall()
E = f"read_parquet('{C_WORK / 'edges.parquet'}')"
con.execute(f"CREATE TABLE p AS SELECT iid, omid, pub_year FROM read_parquet('{C_WORK / 'pubs_slim.parquet'}')")
con.execute(f"""CREATE TABLE ids AS SELECT iid, min(id) FILTER (id_type='doi') doi, min(id) FILTER (id_type='pmid') pmid
                FROM read_parquet('{W / 'idmap.parquet'}') WHERE iid IS NOT NULL GROUP BY 1""")
con.execute(f"""CREATE TABLE rp AS SELECT r.key, r.doi, r.pmid_any AS pmid, r.notice_date, r.paper_year, r.paper_mill,
   rw.reasons, rw.article_type, list_sort(list(DISTINCT p.omid) FILTER (p.omid IS NOT NULL)) AS omids
   FROM read_parquet('{W / f'rw2_{M}.parquet'}') r
   JOIN read_parquet('{W / 'rw_papers_d02_rw_20261101_01.parquet'}') rw USING (key)
   LEFT JOIN read_parquet('{W / f'rw_iid_{M}.parquet'}') ri USING (key) LEFT JOIN p ON p.iid = ri.iid
   GROUP BY ALL""")
con.execute(f"""COPY (SELECT doi, pmid, notice_date AS first_retraction_notice, paper_year, paper_mill,
   array_to_string(reasons, ';') AS rw_reasons, article_type AS rw_article_type, array_to_string(omids, ';') AS oc_omids,
   len(omids) > 0 AS in_graph FROM rp ORDER BY first_retraction_notice, doi NULLS LAST, pmid NULLS LAST, key)
   TO '{rel / 'retracted_papers.csv.gz'}' (HEADER, COMPRESSION gzip)""")
con.execute(f"CREATE TABLE rn AS SELECT DISTINCT iid FROM read_parquet('{W / f'rw_iid_{M}.parquet'}')")
con.execute(f"""COPY (SELECT pa.omid citing_omid, ia.doi citing_doi, ia.pmid citing_pmid, pa.pub_year citing_year,
      pb.omid cited_omid, ib.doi cited_doi, ib.pmid cited_pmid, pb.pub_year cited_year
   FROM (SELECT citing_iid a, cited_iid b FROM {E} WHERE citing_iid IN (SELECT iid FROM rn) OR cited_iid IN (SELECT iid FROM rn)) e
   LEFT JOIN p pa ON pa.iid = e.a LEFT JOIN ids ia ON ia.iid = e.a LEFT JOIN p pb ON pb.iid = e.b LEFT JOIN ids ib ON ib.iid = e.b ORDER BY e.a, e.b)
   TO '{rel / 'citation_edges.csv.gz'}' (HEADER, COMPRESSION gzip)""")
n_c = 0
if COMM:
    nodes = np.load(W / f"d09_node_iids_{COMM}.npy")
    c1 = np.load(W / f"d09_membership_{COMM}_seed1.npy"); c2 = np.load(W / f"d09_membership_{COMM}_seed2.npy")
    assert len(nodes) == len(c1) == len(c2)
    con.register("cm", pd.DataFrame({"iid": nodes, "community_seed1": c1, "community_seed2": c2}))
    con.execute(f"""COPY (SELECT p.omid, i.doi, i.pmid, cm.community_seed1, cm.community_seed2 FROM cm
       LEFT JOIN p USING (iid) LEFT JOIN ids i USING (iid) ORDER BY cm.iid)
       TO '{rel / 'communities.csv.gz'}' (HEADER, COMPRESSION gzip)""")
    n_c = len(nodes)
n_r = q(f"SELECT count(*), count(*) FILTER (in_graph) FROM read_csv('{rel / 'retracted_papers.csv.gz'}')")[0]
n_e = q(f"SELECT count(*) FROM read_csv('{rel / 'citation_edges.csv.gz'}')")[0][0]
(rel / "README.md").write_text(f"""# Retraction-labelled open citation neighbourhoods (biomedical and other fields), v1

Built {run.info['started_utc']} by `d14_dataset.py` (run {sys.argv[1]}).

## Files
- `retracted_papers.csv.gz` ({n_r[0]:,} rows): every Retraction Watch paper with nature "Retraction" in the copy of
  30 Oct 2026 (repository commit a98cc7e), one row per paper (DOI, else PMID): DOI, PMID, date of the first retraction notice,
  publication year, paper-mill flag (any reason containing "Paper Mill"), Retraction Watch reasons and article type,
  OpenCitations OMIDs of the matched graph node(s), and whether it is in the graph ({n_r[1]:,} are).
- `citation_edges.csv.gz` ({n_e:,} rows): every citation in the OpenCitations January 2024 snapshot
  (doi:10.13012/B2IDB-5216575_V1) in which the citing or the cited paper is retracted; both ends with OMID, DOI, PMID and year.

- `communities.csv.gz` ({n_c:,} rows{'' if n_c else '; not built in this run'}): Leiden (modularity, two iterations)
  community of every node in the subgraph used for the concentration analysis (retracted biomedical papers with a journal,
  one non-retracted paper per retracted paper from the same journal and publication year, and all their citation
  neighbours), for seeds 1 and 2 (run {COMM}). Membership in this subgraph says nothing about a paper's status.

## Time split
Retraction dates allow any time point T: papers retracted on or before T are "known"; later ones are outcomes. The graph is
essentially complete to about September 2023.

## What is not included
No author names, titles, abstracts or notes; no scores or rankings of non-retracted papers. A retraction is a public
editorial label and does not imply misconduct.

## Sources and licences
OpenCitations data CC0 / the parsed snapshot CC BY 4.0 (Illinois Data Bank); OpenCitations Meta CC0; Retraction Watch database
distributed by Crossref, CC0 per Crossref's licence table (https://www.crossref.org/documentation/retrieve-metadata/;
Crossref asks that published work cite the source); PubMed identifiers courtesy of the U.S. National Library of Medicine
(may not reflect the latest NLM data). This derived dataset: CC BY 4.0.

## Cite
Please cite the article (Mohasel Arjomandi, *Do links to retracted papers predict future retractions? An out-of-sample
test on the open biomedical citation graph*, submitted) and this dataset. Code and run records:
https://github.com/HosseinMA96/retracted-neighbours-open-data
""")
sums = [f"{sha256(f)}  {f.name}" for f in sorted(rel.iterdir()) if f.is_file()]
(rel / "SHA256SUMS").write_text("\n".join(sums) + "\n")
run.log("release_dir", str(rel)); run.log("retracted_rows", n_r[0]); run.log("retracted_in_graph", n_r[1]); run.log("edge_rows", n_e); run.log("community_rows", n_c)
run.log("files", {f.name: f.stat().st_size for f in rel.iterdir()}); run.log("release_sha256", sums)
run.finish()
