"""D4: parse the whole PubMed 2026 baseline in parallel, then combine into one table (latest file wins per PMID).
usage: python d04_run.py RUN_ID [n_procs]
"""
import sys
from multiprocessing import Pool
from pathlib import Path
import duckdb
from common import Run, D_DATA, sha256
from pubmed_parse import parse_file

RAW = D_DATA / "raw" / "pubmed26"; PART = D_DATA / "work" / "pubmed26_parts"; OUT = D_DATA / "work" / "pubmed26.parquet"
files = sorted(RAW.glob("pubmed26n*.xml.gz"))
missing_ok = [f.name for f in files if not Path(str(f) + ".ok").exists()]
nproc = int(sys.argv[2]) if len(sys.argv) > 2 else 7
run = Run(sys.argv[1], __file__, {"raw": str(RAW), "n_files": len(files), "n_procs": nproc,
                                   "parser_sha256": sha256(Path(__file__).with_name("pubmed_parse.py"))})
if len(files) != 1334 or missing_ok:
    sys.exit(f"baseline incomplete: {len(files)} files, {len(missing_ok)} without .ok")
PART.mkdir(parents=True, exist_ok=True)
with Pool(nproc) as pool:
    stats = [s for _, s in pool.starmap(parse_file, [(f, PART) for f in files]) if s]
run.log("files_parsed_now", len(stats))
run.log("articles_parsed_now", sum(s["articles"] for s in stats))
run.log("delete_citations", sum(s["deleted"] for s in stats))

con = duckdb.connect(); con.execute("SET threads=8; SET memory_limit='40GB'")
q = lambda s: con.execute(s).fetchall()
con.execute(f"""COPY (SELECT * FROM read_parquet('{PART}/*.parquet')
                QUALIFY row_number() OVER (PARTITION BY pmid ORDER BY source_file DESC, pmid_version DESC) = 1)
                TO '{OUT}' (FORMAT parquet, COMPRESSION zstd)""")
P = f"read_parquet('{OUT}')"
run.log("rows_all_files", q(f"SELECT count(*) FROM read_parquet('{PART}/*.parquet')")[0][0])
run.log("distinct_pmid", q(f"SELECT count(*) FROM {P}")[0][0])
run.log("with_doi", q(f"SELECT count(*) FROM {P} WHERE doi IS NOT NULL")[0][0])
run.log("duplicate_doi_values", q(f"SELECT count(*) FROM (SELECT doi FROM {P} WHERE doi IS NOT NULL GROUP BY doi HAVING count(*) > 1)")[0][0])
run.log("with_year", q(f"SELECT count(*) FROM {P} WHERE year IS NOT NULL")[0][0])
run.log("pubtype_retracted_publication_D016441", q(f"SELECT count(*) FROM {P} WHERE list_contains(pub_type_ui, 'D016441')")[0][0])
run.log("pubtype_retraction_of_publication_D016440", q(f"SELECT count(*) FROM {P} WHERE list_contains(pub_type_ui, 'D016440')")[0][0])
run.log("cc_reftype_counts", dict(q(f"SELECT r, count(*) FROM (SELECT unnest(cc_reftype) r FROM {P}) WHERE r LIKE 'Retraction%' OR r LIKE 'ExpressionOfConcern%' OR r LIKE 'Erratum%' GROUP BY 1")))
run.log("with_retractionin", q(f"SELECT count(*) FROM {P} WHERE list_contains(cc_reftype, 'RetractionIn')")[0][0])
run.log("with_any_grant", q(f"SELECT count(*) FROM {P} WHERE len(grant_agency) > 0")[0][0])
run.log("with_nih_agency", q(f"SELECT count(*) FROM {P} WHERE len(list_filter(grant_agency, a -> a LIKE '%NIH%')) > 0")[0][0])
run.log("top_agencies", q(f"SELECT a, count(*) n FROM (SELECT unnest(grant_agency) a FROM {P}) GROUP BY 1 ORDER BY n DESC LIMIT 40"))
run.log("rows_by_year_decade", dict(q(f"SELECT (year // 10) * 10, count(*) FROM {P} GROUP BY 1 ORDER BY 1")))
run.log("output", {"path": str(OUT), "bytes": OUT.stat().st_size})
run.finish()
