"""D11 (RQ4): citations per year around the retraction year, retracted biomedical papers vs matched controls.
Retracted: first Retraction Watch notice 2000-2021, biomedical, with a journal, published <= notice year.
Control: one non-retracted biomedical paper from the same journal and publication year, chosen deterministically (lowest hash(iid, 20261101) within journal x year).
Relative year k = citing pub_year - notice year, k in [-5, 2] (snapshot ends 2023). Aggregates only.
usage: python d11_event.py RUN_ID MATCH_RUN_ID
"""
import sys, duckdb, pandas as pd
from common import Run, C_WORK, D_DATA

W = D_DATA / "work"; M = sys.argv[2]; SEED = 20261101   # hash seed for deterministic control choice
run = Run(sys.argv[1], __file__, {"match_run": M, "notice_years": [2000, 2021], "k": [-5, 2], "seed": SEED})
con = duckdb.connect(); con.execute(f"SET threads=8; SET memory_limit='48GB'; SET temp_directory='{W / 'tmp'}'")
q = lambda s: con.execute(s).fetchall()
E = f"read_parquet('{C_WORK / 'edges.parquet'}')"
con.execute(f"CREATE TABLE idm AS SELECT iid, id_type, id FROM read_parquet('{W / 'idmap.parquet'}') WHERE iid IS NOT NULL")
con.execute(f"""CREATE TABLE bio AS SELECT DISTINCT iid FROM idm WHERE id_type='pmid'
   UNION SELECT DISTINCT i.iid FROM idm i JOIN (SELECT DISTINCT doi FROM read_parquet('{W / 'pubmed26.parquet'}') WHERE doi IS NOT NULL) d
   ON i.id_type='doi' AND i.id=d.doi""")
con.execute(f"""CREATE TABLE node AS SELECT b.iid, p.pub_year, j.journal_id FROM bio b JOIN read_parquet('{C_WORK / 'pubs_slim.parquet'}') p USING (iid)
   JOIN read_parquet('{C_WORK / 'pubs_j.parquet'}') j USING (iid)""")
con.execute(f"""CREATE TABLE ret AS SELECT ri.iid, year(min(r.notice_date)) ry, bool_or(r.paper_mill) mill
   FROM read_parquet('{W / f'rw_iid_{M}.parquet'}') ri JOIN read_parquet('{W / f'rw2_{M}.parquet'}') r USING (key) GROUP BY 1""")
con.execute("""CREATE TABLE tr AS SELECT n.iid, n.pub_year, n.journal_id, ret.ry, ret.mill FROM node n JOIN ret USING (iid)
               WHERE ret.ry BETWEEN 2000 AND 2021 AND n.pub_year <= ret.ry""")
con.execute("""CREATE TABLE pool AS SELECT iid, pub_year, journal_id, hash(iid, 20261101) u FROM node
               WHERE (journal_id, pub_year) IN (SELECT journal_id, pub_year FROM tr) AND iid NOT IN (SELECT iid FROM ret)""")
con.execute("""CREATE TABLE tr2 AS SELECT *, row_number() OVER (PARTITION BY journal_id, pub_year ORDER BY iid) rk FROM tr""")
con.execute("""CREATE TABLE pool2 AS SELECT *, row_number() OVER (PARTITION BY journal_id, pub_year ORDER BY u, iid) rk FROM pool""")
con.execute("""CREATE TABLE pairs AS SELECT t.iid r_iid, p.iid c_iid, t.ry, t.mill, t.pub_year FROM tr2 t
               JOIN pool2 p USING (journal_id, pub_year, rk)""")
run.log("retracted_eligible", q("SELECT count(*) FROM tr")[0][0])
run.log("matched_pairs", q("SELECT count(*) FROM pairs")[0][0])
con.execute("""CREATE TABLE grp AS SELECT r_iid iid, ry, mill, 'retracted' arm FROM pairs
               UNION ALL SELECT c_iid, ry, mill, 'control' FROM pairs""")
res = pd.DataFrame(q(f"""SELECT g.arm, g.mill, p.pub_year - g.ry k, count(*) cites FROM {E} e
   JOIN grp g ON e.cited_iid = g.iid JOIN read_parquet('{C_WORK / 'pubs_slim.parquet'}') p ON p.iid = e.citing_iid
   WHERE p.pub_year - g.ry BETWEEN -5 AND 2 GROUP BY ALL"""), columns=["arm", "mill", "k", "cites"])
npairs = dict(q("SELECT mill, count(*) FROM pairs GROUP BY 1"))
res["per_paper"] = res.apply(lambda r: r.cites / npairs[r.mill], axis=1)
res.sort_values(["mill", "arm", "k"]).to_csv(run.dir / "citations_by_relative_year.csv", index=False)
a = res.groupby(["arm", "k"]).cites.sum().unstack(0); a = a / sum(npairs.values()); a["ratio"] = a.retracted / a.control
run.log("per_paper_all", a.round(4).reset_index().to_dict("records"))
run.log("pairs_by_mill", {str(k): v for k, v in npairs.items()})
run.finish()
