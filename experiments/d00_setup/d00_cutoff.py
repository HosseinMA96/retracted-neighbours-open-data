"""D0b: empirical cutoff of the Jan 2024 snapshot. Counts Meta records and citing edges by publication month
around the end of 2023. Read-only.
usage: python d00_cutoff.py RUN_ID
"""
import os, sys, duckdb
from common import Run, C_WORK

META = os.environ.get("META_DIR", "/home/azureuser/c/data/raw/meta_csv")
run = Run(sys.argv[1], __file__, {"meta_dir": META, "edges": str(C_WORK / "edges.parquet")})
con = duckdb.connect(); con.execute("SET threads=8; SET memory_limit='48GB'")
q = lambda s: con.execute(s).fetchall()
con.execute(f"""CREATE TEMP TABLE m AS SELECT regexp_extract(id, 'omid:(br/[0-9]+)', 1) omid, left(pub_date, 7) ym
               FROM read_csv('{META}/*.csv', header=true, all_varchar=true) WHERE pub_date >= '2023-01'""")
run.log("meta_records_by_month_2023_on", dict(q("SELECT ym, count(*) FROM m WHERE length(ym)=7 GROUP BY 1 ORDER BY 1")))
con.execute(f"CREATE TEMP TABLE p AS SELECT iid, omid FROM read_parquet('{C_WORK / 'pubs_slim.parquet'}')")
run.log("citing_edges_by_citing_month_2023_on", dict(q(f"""
    SELECT m.ym, count(*) FROM read_parquet('{C_WORK / 'edges.parquet'}') e
    JOIN p ON e.citing_iid = p.iid JOIN m USING (omid) WHERE length(m.ym)=7 GROUP BY 1 ORDER BY 1""")))
run.finish()
