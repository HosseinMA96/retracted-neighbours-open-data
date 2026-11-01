"""D10 (RQ3): how often NIH-funded biomedical papers cite a paper after its retraction, vs non-NIH papers.
Post-retraction citation: citing pub_year > year of the cited paper's first Retraction Watch notice
(the convention of Hsiao & Schneider's Data Bank dataset: after the calendar year of retraction).
NIH-funded: a PubMed grant whose agency contains "NIH". Aggregates only.
usage: python d10_nih.py RUN_ID MATCH_RUN_ID
"""
import sys, duckdb, numpy as np, pandas as pd
from common import Run, C_WORK, D_DATA

W = D_DATA / "work"; M = sys.argv[2]
run = Run(sys.argv[1], __file__, {"match_run": M, "citing_years": [2000, 2023], "nih_rule": "grant_agency LIKE '%NIH%'"})
con = duckdb.connect(); con.execute(f"SET threads=8; SET memory_limit='48GB'; SET temp_directory='{W / 'tmp'}'")
q = lambda s: con.execute(s).fetchall()
E = f"read_parquet('{C_WORK / 'edges.parquet'}')"

con.execute(f"""CREATE TABLE pm AS SELECT pmid, doi, len(list_filter(grant_agency, a -> a LIKE '%NIH%')) > 0 AS nih,
                len(grant_agency) > 0 AS any_grant FROM read_parquet('{W / 'pubmed26.parquet'}')""")
con.execute(f"CREATE TABLE idm AS SELECT iid, id_type, id FROM read_parquet('{W / 'idmap.parquet'}') WHERE iid IS NOT NULL")
# node -> PubMed record (via Meta PMID, else via DOI)
con.execute("""CREATE TABLE np AS
   SELECT iid, bool_or(nih) AS nih, bool_or(any_grant) AS any_grant FROM (
     SELECT i.iid, pm.nih, pm.any_grant FROM idm i JOIN pm ON i.id_type='pmid' AND CAST(i.id AS BIGINT) = pm.pmid
     UNION ALL
     SELECT i.iid, pm.nih, pm.any_grant FROM idm i JOIN pm ON i.id_type='doi' AND i.id = pm.doi) GROUP BY 1""")
con.execute(f"""CREATE TABLE cit AS SELECT np.iid, p.pub_year, j.journal_id, np.nih, np.any_grant FROM np
   JOIN read_parquet('{C_WORK / 'pubs_slim.parquet'}') p USING (iid) LEFT JOIN read_parquet('{C_WORK / 'pubs_j.parquet'}') j USING (iid)
   WHERE p.pub_year BETWEEN 2000 AND 2023""")
run.log("biomedical_papers_2000_2023", q("SELECT count(*) FROM cit")[0][0])
run.log("nih_funded_2000_2023", q("SELECT count(*) FROM cit WHERE nih")[0][0])
con.execute(f"""CREATE TABLE ret AS SELECT ri.iid, year(min(r.notice_date)) AS ry, bool_or(r.paper_mill) AS mill
   FROM read_parquet('{W / f'rw_iid_{M}.parquet'}') ri JOIN read_parquet('{W / f'rw2_{M}.parquet'}') r USING (key) GROUP BY 1""")
con.execute(f"""CREATE TABLE pr AS SELECT e.citing_iid AS iid, e.cited_iid, ret.ry, ret.mill, c.pub_year
   FROM {E} e JOIN ret ON e.cited_iid = ret.iid JOIN cit c ON c.iid = e.citing_iid
   WHERE c.pub_year > ret.ry AND e.citing_iid NOT IN (SELECT iid FROM ret)""")   # citing paper not itself retracted
run.log("post_retraction_citations", q("SELECT count(*) FROM pr")[0][0])
run.log("post_retraction_citations_from_nih", q("SELECT count(*) FROM pr JOIN cit USING (iid) WHERE cit.nih")[0][0])
run.log("retracted_papers_cited_after_retraction", q("SELECT count(DISTINCT cited_iid) FROM pr")[0][0])
run.log("retracted_papers_cited_after_retraction_by_nih", q("SELECT count(DISTINCT cited_iid) FROM pr JOIN cit USING (iid) WHERE cit.nih")[0][0])
con.execute("""CREATE TABLE expo AS SELECT c.*, pr.iid IS NOT NULL AS e, coalesce(pr.any_mill, false) AS e_mill FROM cit c
   LEFT JOIN (SELECT iid, bool_or(mill) any_mill FROM pr GROUP BY 1) pr USING (iid)
   WHERE c.iid NOT IN (SELECT iid FROM ret)""")
by = pd.DataFrame(q("""SELECT pub_year, nih, count(*) n, count(*) FILTER (e) k, count(*) FILTER (e_mill) k_mill FROM expo
                       GROUP BY ALL ORDER BY ALL"""), columns=["pub_year", "nih", "n", "k", "k_mill"])
by["share"] = by.k / by.n
by.to_csv(run.dir / "exposure_by_year_nih.csv", index=False)
tot = by.groupby("nih")[["n", "k", "k_mill"]].sum(); tot["share"] = tot.k / tot.n
run.log("overall_by_nih", tot.reset_index().to_dict("records"))
for y0, y1 in [(2015, 2023), (2020, 2023)]:
    t = by[by.pub_year.between(y0, y1)].groupby("nih")[["n", "k"]].sum(); t["share"] = t.k / t.n
    run.log(f"by_nih_{y0}_{y1}", t.reset_index().to_dict("records"))
# Within journal x year: Mantel-Haenszel OR of NIH funding on post-retraction citing (RGB CI)
g = pd.DataFrame(q("""SELECT journal_id, pub_year, count(*) n, count(*) FILTER (nih) n1, count(*) FILTER (e) pos,
                      count(*) FILTER (nih AND e) a FROM expo WHERE journal_id IS NOT NULL GROUP BY 1, 2"""),
                 columns=["j", "y", "n", "n1", "pos", "a"])
n0 = g.n - g.n1; c = g.pos - g.a; b = g.n1 - g.a; d = n0 - c; inf = (g.n1 > 0) & (n0 > 0) & (g.pos > 0)
a_, b_, c_, d_, n_ = (x[inf].astype(float) for x in (g.a, b, c, d, g.n))
R, S, P, Q = a_ * d_ / n_, b_ * c_ / n_, (a_ + d_) / n_, (b_ + c_) / n_
orr = R.sum() / S.sum()
v = (P * R).sum() / (2 * R.sum() ** 2) + (P * S + Q * R).sum() / (2 * R.sum() * S.sum()) + (Q * S).sum() / (2 * S.sum() ** 2)
run.log("mh_or_nih_on_postretraction_citing_within_journal_year", {"or": orr, "lo": orr * np.exp(-1.96 * v ** .5),
        "hi": orr * np.exp(1.96 * v ** .5), "strata_informative": int(inf.sum())})
run.finish()
