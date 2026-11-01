"""D12: label-quality checks (protocol fixed before running; see RESULTS_LOG).
(1) Match precision: 300 DOI-keyed Retraction Watch papers matched to graph nodes, drawn with seed 20261101; compare the
    Retraction Watch title with the OpenCitations Meta title (token Jaccard after lower-casing and stripping
    punctuation). Thresholds fixed in advance: >= 0.8 same; 0.5-0.8 check; < 0.5 suspect. Suspects are listed
    (DOI + both titles; public records) for reading.
(2) PubMed-flagged papers absent from Retraction Watch: notice publication years and journals (top 10 by count).
usage: python d12_check.py RUN_ID MATCH_RUN_ID
"""
import os, re, sys, duckdb, pandas as pd
from common import Run, D_DATA

W = D_DATA / "work"; M = sys.argv[2]; META = os.environ.get("META_DIR", "/home/azureuser/c/data/raw/meta_csv")
RWCSV = D_DATA / "raw/retraction-watch-data/retraction_watch.csv"
run = Run(sys.argv[1], __file__, {"match_run": M, "n": 300, "seed": 20261101, "thresholds": [0.5, 0.8]})
con = duckdb.connect(); con.execute(f"SET threads=8; SET memory_limit='40GB'; SET temp_directory='{W / 'tmp'}'")
q = lambda s: con.execute(s).fetchall()
rw = pd.read_csv(RWCSV, dtype=str, keep_default_na=False, usecols=["Record ID", "Title", "OriginalPaperDOI", "RetractionNature"])
rw = rw[rw.RetractionNature == "Retraction"]
con.register("rwt", rw)
s = con.execute(f"""SELECT DISTINCT ON (ri.key) ri.key, ri.iid FROM read_parquet('{W / f'rw_iid_{M}.parquet'}') ri ORDER BY ri.key, ri.iid""").df().sort_values("key", kind="stable").reset_index(drop=True)
s = s[~s.key.str.startswith("pmid:")].sample(n=300, random_state=20261101)   # DOI-keyed papers (titles joinable)
con.register("smp", s)
con.execute(f"""CREATE TABLE om AS SELECT s.key, s.iid, p.omid FROM smp s
   JOIN read_parquet('/home/azureuser/c/data/work/c6_full_20261031_02/pubs_slim.parquet') p USING (iid)""")
mt = con.execute(f"""SELECT regexp_extract(id, 'omid:(br/[0-9]+)', 1) omid, title FROM read_csv('{META}/*.csv', header=true, all_varchar=true)
   WHERE regexp_extract(id, 'omid:(br/[0-9]+)', 1) IN (SELECT omid FROM om)""").df()
om = con.execute("SELECT * FROM om").df().merge(mt, on="omid", how="left")
rwt = rw.assign(key=rw.OriginalPaperDOI.str.strip().str.lower()).drop_duplicates("key")[["key", "Title"]]
om = om.merge(rwt, on="key", how="left")
tok = lambda t: set(re.sub(r"[^a-z0-9 ]", " ", str(t).lower()).split())
def jac(a, b):
    A, B = tok(a), tok(b); return len(A & B) / len(A | B) if A | B else 0.0
om["jaccard"] = [jac(a, b) for a, b in zip(om.Title, om.title)]
om["class"] = pd.cut(om.jaccard, [-0.01, 0.5, 0.8, 1.01], labels=["suspect", "check", "same"])
run.log("sample", len(om)); run.log("meta_title_found", int(om.title.notna().sum())); run.log("rw_title_found", int(om.Title.notna().sum()))
run.log("classes", om["class"].value_counts().to_dict())
om[om["class"] != "same"][["key", "jaccard", "Title", "title"]].to_csv(run.dir / "non_same_matches.csv", index=False)
pm = f"read_parquet('{W / 'pubmed26.parquet'}')"
con.execute(f"""CREATE TABLE only_pm AS SELECT pmid, doi, nlm_id, journal_abbrev, cc_reftype, cc_pmid FROM {pm}
   WHERE list_contains(pub_type_ui, 'D016441')
   AND pmid NOT IN (SELECT pmid_any FROM read_parquet('{W / f'rw2_{M}.parquet'}') WHERE pmid_any IS NOT NULL)
   AND (doi IS NULL OR doi NOT IN (SELECT doi FROM read_parquet('{W / f'rw2_{M}.parquet'}') WHERE doi IS NOT NULL))""")
run.log("pubmed_only_flagged", q("SELECT count(*) FROM only_pm")[0][0])
run.log("pubmed_only_with_doi", q("SELECT count(*) FROM only_pm WHERE doi IS NOT NULL")[0][0])
run.log("pubmed_only_notice_year", q(f"""SELECT n.year, count(DISTINCT o.pmid) FROM only_pm o,
   unnest(list_filter(list_zip(o.cc_reftype, o.cc_pmid), x -> x[1] = 'RetractionIn')) t(z) JOIN {pm} n ON n.pmid = z[2]
   GROUP BY 1 ORDER BY 1"""))
run.log("pubmed_only_top_journals", q("SELECT journal_abbrev, count(*) n FROM only_pm GROUP BY 1 ORDER BY n DESC LIMIT 10"))
run.finish()
