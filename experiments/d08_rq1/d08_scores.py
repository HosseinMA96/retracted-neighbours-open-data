"""D8a: compute and FREEZE the pre-registered scores (PREREGISTRATION.md §4) for three settings.
Reads only retraction notices dated <= the setting's time point. No outcome is computed here.
Per-paper tables stay on the VM (~/d/data/work/d08/); the run folder gets their sha256 and aggregate counts.
usage: python d08_scores.py RUN_ID MATCH_RUN_ID
"""
import sys, duckdb
from common import Run, C_WORK, D_DATA, sha256

W = D_DATA / "work"; M = sys.argv[2]
SETTINGS = {  # name: (time point, first pub_year, last pub_year)
    "main_T0": ("2024-01-31", 2015, 2023),
    "sens_T0p": ("2023-09-30", 2015, 2023),
    "train_Tm1": ("2021-12-31", 2013, 2021),
}
M_PRIOR = 100
run = Run(sys.argv[1], __file__, {"settings": SETTINGS, "m_prior": M_PRIOR, "match_run": M,
                                   "prereg_sha256": sha256(W.parent.parent / "experiments/d07_prereg/PREREGISTRATION.md")
                                   if (W.parent.parent / "experiments/d07_prereg/PREREGISTRATION.md").exists() else None})
out_dir = W / "d08" / sys.argv[1]; out_dir.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(); con.execute(f"SET threads=8; SET memory_limit='48GB'; SET temp_directory='{W / 'tmp'}'")
q = lambda s: con.execute(s).fetchall()
E = f"read_parquet('{C_WORK / 'edges.parquet'}')"

con.execute(f"CREATE TABLE idm AS SELECT iid, id_type, id FROM read_parquet('{W / 'idmap.parquet'}') WHERE iid IS NOT NULL")
con.execute(f"""CREATE TABLE bio AS SELECT DISTINCT iid FROM idm WHERE id_type = 'pmid'
   UNION SELECT DISTINCT i.iid FROM idm i JOIN (SELECT DISTINCT doi FROM read_parquet('{W / 'pubmed26.parquet'}') WHERE doi IS NOT NULL) d
   ON i.id_type = 'doi' AND i.id = d.doi""")
con.execute("""CREATE TABLE dup AS SELECT DISTINCT iid FROM idm WHERE id_type='doi' AND id IN
               (SELECT id FROM idm WHERE id_type='doi' GROUP BY id HAVING count(DISTINCT iid) > 1)""")
con.execute(f"""CREATE TABLE node AS SELECT b.iid, p.pub_year, j.journal_id FROM bio b
   JOIN read_parquet('{C_WORK / 'pubs_slim.parquet'}') p USING (iid) LEFT JOIN read_parquet('{C_WORK / 'pubs_j.parquet'}') j USING (iid)""")
# Retraction status per iid: first notice date and paper-mill flag (any matched Retraction Watch paper)
con.execute(f"""CREATE TABLE st AS SELECT ri.iid, min(r.notice_date) AS first_notice, bool_or(r.paper_mill) AS mill
   FROM read_parquet('{W / f'rw_iid_{M}.parquet'}') ri JOIN read_parquet('{W / f'rw2_{M}.parquet'}') r USING (key) GROUP BY 1""")
run.log("biomedical_nodes", q("SELECT count(*) FROM node")[0][0])
run.log("biomedical_nodes_with_journal", q("SELECT count(*) FROM node WHERE journal_id IS NOT NULL")[0][0])
run.log("dup_doi_iids", q("SELECT count(*) FROM dup")[0][0])

for name, (T, y0, y1) in SETTINGS.items():
    yT = int(T[:4])
    con.execute(f"CREATE OR REPLACE TABLE R AS SELECT iid, mill FROM st WHERE first_notice <= DATE '{T}'")
    con.execute(f"""CREATE OR REPLACE TABLE cand AS SELECT n.iid, n.pub_year, n.journal_id FROM node n
        WHERE n.pub_year BETWEEN {y0} AND {y1} AND n.journal_id IS NOT NULL AND n.iid NOT IN (SELECT iid FROM R)""")
    con.execute(f"""CREATE OR REPLACE TABLE outd AS SELECT e.citing_iid AS iid, count(*) AS out_deg,
        count(r.iid) AS s1, count(r.iid) FILTER (r.mill) AS s4
        FROM {E} e JOIN cand c ON e.citing_iid = c.iid LEFT JOIN R r ON e.cited_iid = r.iid GROUP BY 1""")
    con.execute(f"""CREATE OR REPLACE TABLE ind AS SELECT e.cited_iid AS iid, count(*) AS s3
        FROM {E} e JOIN R r ON e.citing_iid = r.iid JOIN cand c ON e.cited_iid = c.iid GROUP BY 1""")
    ylast = min(yT, 2023)
    con.execute(f"""CREATE OR REPLACE TABLE jb AS SELECT journal_id, count(*) n_j, count(R.iid) r_j FROM node
        LEFT JOIN R USING (iid) WHERE journal_id IS NOT NULL AND pub_year BETWEEN 2010 AND {ylast} GROUP BY 1""")
    g = q("SELECT sum(r_j)::DOUBLE / sum(n_j) FROM jb")[0][0]
    out = out_dir / f"scores_{name}.parquet"
    con.execute(f"""COPY (SELECT c.iid, c.pub_year, c.journal_id, {yT} - c.pub_year AS age, o.out_deg,
            o.s1, o.s1::DOUBLE / o.out_deg AS s2, coalesce(i.s3, 0) AS s3, o.s4,
            (jb.r_j + {M_PRIOR} * {g}) / (jb.n_j + {M_PRIOR}) AS b, c.iid IN (SELECT iid FROM dup) AS dup_doi
        FROM cand c JOIN outd o USING (iid) LEFT JOIN ind i USING (iid) JOIN jb USING (journal_id))
        TO '{out}' (FORMAT parquet, COMPRESSION zstd)""")
    S = f"read_parquet('{out}')"
    run.log(f"{name}", {
        "T": T, "pub_years": [y0, y1], "R_size": q("SELECT count(*) FROM R")[0][0], "global_rate_g": g,
        "candidates_with_journal": q("SELECT count(*) FROM cand")[0][0],
        "scored_candidates_out_deg_ge1": q(f"SELECT count(*) FROM {S}")[0][0],
        "s1_ge1": q(f"SELECT count(*) FROM {S} WHERE s1 >= 1")[0][0],
        "s3_ge1": q(f"SELECT count(*) FROM {S} WHERE s3 >= 1")[0][0],
        "s4_ge1": q(f"SELECT count(*) FROM {S} WHERE s4 >= 1")[0][0],
        "s1_dist": dict(q(f"SELECT CASE WHEN s1>=5 THEN '5+' WHEN s1>=3 THEN '3-4' ELSE s1::VARCHAR END k, count(*) FROM {S} GROUP BY 1 ORDER BY 1")),
        "dup_doi": q(f"SELECT count(*) FROM {S} WHERE dup_doi")[0][0],
        "journals": q(f"SELECT count(DISTINCT journal_id) FROM {S}")[0][0],
        "file": str(out), "sha256": sha256(out)})
run.finish()
