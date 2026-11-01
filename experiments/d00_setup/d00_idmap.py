"""D0: identifier map for the Jan 2024 OpenCitations graph.
OpenCitations Meta CSV dump (Figshare v7) -> (omid, doi, pmid); joined to the Data Bank pubs table (omid -> iid).
Output (large, stays on the VM): $D_DATA/work/idmap.parquet. Run folder gets counts only.
usage: python d00_idmap.py RUN_ID
"""
import os, sys, duckdb
from common import Run, C_WORK, D_DATA

META = os.environ.get("META_DIR", "/home/azureuser/c/data/raw/meta_csv")
run = Run(sys.argv[1], __file__, {"meta_dir": META, "pubs_slim": str(C_WORK / "pubs_slim.parquet"),
                                   "threads": 8, "memory_limit": "48GB"})
out = D_DATA / "work" / "idmap.parquet"; out.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(); con.execute("SET threads=8; SET memory_limit='48GB'; SET preserve_insertion_order=false")
con.execute(f"SET temp_directory='{D_DATA / 'work' / 'tmp'}'")
q = lambda s: con.execute(s).fetchall()

con.execute(f"""
CREATE TEMP TABLE meta AS
SELECT regexp_extract(id, 'omid:(br/[0-9]+)', 1)                            AS omid,
       regexp_extract_all(lower(id), 'doi:(\\S+)', 1)                        AS dois,
       regexp_extract_all(id, 'pmid:([0-9]+)', 1)                            AS pmids,
       type, pub_date
FROM read_csv('{META}/*.csv', header=true, all_varchar=true, parallel=true,
              columns={{'id':'VARCHAR','title':'VARCHAR','author':'VARCHAR','issue':'VARCHAR','volume':'VARCHAR',
                        'venue':'VARCHAR','page':'VARCHAR','pub_date':'VARCHAR','type':'VARCHAR','publisher':'VARCHAR',
                        'editor':'VARCHAR'}})""")
run.log("meta_rows", q("SELECT count(*) FROM meta")[0][0])
run.log("meta_rows_no_omid", q("SELECT count(*) FROM meta WHERE omid = ''")[0][0])
run.log("meta_distinct_omid", q("SELECT count(DISTINCT omid) FROM meta")[0][0])
run.log("meta_with_doi", q("SELECT count(*) FROM meta WHERE len(dois) > 0")[0][0])
run.log("meta_with_multiple_doi", q("SELECT count(*) FROM meta WHERE len(dois) > 1")[0][0])
run.log("meta_with_pmid", q("SELECT count(*) FROM meta WHERE len(pmids) > 0")[0][0])
run.log("meta_with_multiple_pmid", q("SELECT count(*) FROM meta WHERE len(pmids) > 1")[0][0])

# Long form: one row per (omid, id_type, id). Joined to iid through the pubs table.
con.execute(f"""
COPY (
  WITH p AS (SELECT iid, omid, pub_year, type AS pubs_type FROM read_parquet('{C_WORK / 'pubs_slim.parquet'}')),
  ids AS (SELECT omid, 'doi' AS id_type, unnest(dois) AS id FROM meta
          UNION ALL SELECT omid, 'pmid', unnest(pmids) FROM meta)
  SELECT p.iid, ids.omid, ids.id_type, ids.id, p.pub_year, p.pubs_type
  FROM ids LEFT JOIN p USING (omid)
) TO '{out}' (FORMAT parquet, COMPRESSION zstd)""")
m = f"read_parquet('{out}')"
run.log("idmap_rows", q(f"SELECT count(*) FROM {m}")[0][0])
run.log("idmap_rows_by_type", dict(q(f"SELECT id_type, count(*) FROM {m} GROUP BY 1")))
run.log("idmap_rows_with_iid_by_type", dict(q(f"SELECT id_type, count(*) FROM {m} WHERE iid IS NOT NULL GROUP BY 1")))
run.log("distinct_iid_with_pmid", q(f"SELECT count(DISTINCT iid) FROM {m} WHERE id_type='pmid' AND iid IS NOT NULL")[0][0])
run.log("distinct_iid_with_doi", q(f"SELECT count(DISTINCT iid) FROM {m} WHERE id_type='doi' AND iid IS NOT NULL")[0][0])
run.log("pmid_mapping_to_several_iid", q(f"""SELECT count(*) FROM (SELECT id FROM {m} WHERE id_type='pmid' AND iid IS NOT NULL
                                             GROUP BY id HAVING count(DISTINCT iid) > 1)""")[0][0])
run.log("doi_mapping_to_several_iid", q(f"""SELECT count(*) FROM (SELECT id FROM {m} WHERE id_type='doi' AND iid IS NOT NULL
                                            GROUP BY id HAVING count(DISTINCT iid) > 1)""")[0][0])
run.log("pubs_rows", q(f"SELECT count(*) FROM read_parquet('{C_WORK / 'pubs_slim.parquet'}')")[0][0])
run.log("pubs_omid_not_in_meta", q(f"""SELECT count(*) FROM read_parquet('{C_WORK / 'pubs_slim.parquet'}') p
                                       ANTI JOIN meta USING (omid)""")[0][0])
run.log("pmid_iid_by_pub_year_decade", dict(q(f"""SELECT (pub_year // 10) * 10 AS dec, count(DISTINCT iid) FROM {m}
            WHERE id_type='pmid' AND iid IS NOT NULL GROUP BY 1 ORDER BY 1""")))
run.log("idmap_parquet", {"path": str(out), "bytes": out.stat().st_size})
run.finish()
