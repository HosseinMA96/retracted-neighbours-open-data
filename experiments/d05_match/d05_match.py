"""D5: match Retraction Watch papers to graph nodes (iids); cross-check with PubMed; graph coverage; population sizes.
Labels and coverage only. NO scores are computed and exposure is NOT cross-tabulated with post-T0 outcomes
(that waits for the pre-registration, D7).
usage: python d05_match.py RUN_ID RW_RUN_ID
"""
import sys, duckdb
from common import Run, C_WORK, D_DATA

T0 = "2024-01-31"   # provisional; see d00_cutoff
W = D_DATA / "work"
RW = W / f"rw_papers_{sys.argv[2]}.parquet"; IDM = W / "idmap.parquet"; PM = W / "pubmed26.parquet"
E = C_WORK / "edges.parquet"; PUBS = C_WORK / "pubs_slim.parquet"
run = Run(sys.argv[1], __file__, {"T0": T0, "rw": str(RW), "idmap": str(IDM), "pubmed": str(PM), "edges": str(E)})
con = duckdb.connect(); con.execute(f"SET threads=8; SET memory_limit='48GB'; SET temp_directory='{W / 'tmp'}'")
q = lambda s: con.execute(s).fetchall()
one = lambda s: q(s)[0][0]

con.execute(f"CREATE TABLE rw AS SELECT key, doi, pmid, notice_date, paper_year, paper_mill, biomed_subject, reinstated FROM read_parquet('{RW}')")
con.execute(f"CREATE TABLE idm AS SELECT iid, id_type, id FROM read_parquet('{IDM}') WHERE iid IS NOT NULL")
con.execute(f"CREATE TABLE pm AS SELECT pmid, doi, year, pub_type_ui, cc_reftype, cc_pmid, len(list_filter(grant_agency, a -> a LIKE '%NIH%')) > 0 AS nih FROM read_parquet('{PM}')")

# --- 1. Retraction Watch -> PubMed (fill PMIDs from DOIs) --------------------------------------------------
con.execute("""CREATE TABLE rw2 AS SELECT rw.*, CAST(coalesce(CAST(rw.pmid AS BIGINT), pd.pmid) AS BIGINT) AS pmid_any, (rw.pmid IS NULL AND pd.pmid IS NOT NULL) AS pmid_from_pubmed
               FROM rw LEFT JOIN (SELECT doi, min(pmid) pmid FROM pm WHERE doi IS NOT NULL GROUP BY doi) pd ON rw.doi = pd.doi""")
run.log("rw_papers", one("SELECT count(*) FROM rw2"))
run.log("rw_pmid_given", one("SELECT count(*) FROM rw2 WHERE pmid IS NOT NULL"))
run.log("rw_pmid_filled_from_pubmed_doi", one("SELECT count(*) FROM rw2 WHERE pmid_from_pubmed"))
run.log("rw_pmid_given_not_in_pubmed26", one("SELECT count(*) FROM rw2 ANTI JOIN pm USING (pmid) WHERE rw2.pmid IS NOT NULL"))

# --- 2. Cross-check with the PubMed retraction flags -------------------------------------------------------
con.execute("""CREATE TABLE pmr AS SELECT pmid, doi, list_contains(pub_type_ui, 'D016441') AS pt_retracted,
               list_contains(cc_reftype, 'RetractionIn') AS has_retraction_in FROM pm
               WHERE list_contains(pub_type_ui, 'D016441') OR list_contains(cc_reftype, 'RetractionIn')""")
run.log("pubmed_flagged_retracted", one("SELECT count(*) FROM pmr"))
run.log("pubmed_flag_breakdown", q("SELECT pt_retracted, has_retraction_in, count(*) FROM pmr GROUP BY ALL ORDER BY ALL"))
run.log("rw_with_pmid_any", one("SELECT count(*) FROM rw2 WHERE pmid_any IS NOT NULL"))
run.log("rw_with_pmid_any_flagged_in_pubmed", one("SELECT count(*) FROM rw2 SEMI JOIN pmr ON rw2.pmid_any = pmr.pmid"))
run.log("rw_with_pmid_any_flagged_by_notice_year", q("""SELECT year(notice_date) y, count(*) n, count(pmr.pmid) flagged FROM rw2
         LEFT JOIN pmr ON rw2.pmid_any = pmr.pmid WHERE pmid_any IS NOT NULL AND y >= 2015 GROUP BY 1 ORDER BY 1"""))
run.log("pubmed_flagged_not_in_rw", one("""SELECT count(*) FROM pmr WHERE pmid NOT IN (SELECT pmid_any FROM rw2 WHERE pmid_any IS NOT NULL)
         AND (doi IS NULL OR doi NOT IN (SELECT doi FROM rw2 WHERE doi IS NOT NULL))"""))

# --- 3. Retraction Watch -> graph nodes -------------------------------------------------------------------
con.execute("""CREATE TABLE rw_iid AS
   SELECT DISTINCT r.key, i.iid, 'doi' AS via FROM rw2 r JOIN idm i ON i.id_type='doi' AND i.id = r.doi
   UNION ALL
   SELECT DISTINCT r.key, i.iid, 'pmid' FROM rw2 r JOIN idm i ON i.id_type='pmid' AND i.id = CAST(CAST(r.pmid_any AS BIGINT) AS VARCHAR)""")
run.log("rw_matched_by_doi", one("SELECT count(DISTINCT key) FROM rw_iid WHERE via='doi'"))
run.log("rw_matched_by_pmid", one("SELECT count(DISTINCT key) FROM rw_iid WHERE via='pmid'"))
run.log("rw_matched_any", one("SELECT count(DISTINCT key) FROM rw_iid"))
run.log("rw_papers_with_several_iids", one("SELECT count(*) FROM (SELECT key FROM rw_iid GROUP BY key HAVING count(DISTINCT iid) > 1)"))
run.log("iids_shared_by_several_rw_papers", one("SELECT count(*) FROM (SELECT iid FROM rw_iid GROUP BY iid HAVING count(DISTINCT key) > 1)"))
run.log("rw_matched_by_period", q(f"""SELECT notice_date <= DATE '{T0}' AS by_T0, count(*) n, count(m.key) n_matched FROM rw2
         LEFT JOIN (SELECT DISTINCT key FROM rw_iid) m USING (key) GROUP BY 1 ORDER BY 1"""))

# --- 4. Graph degrees of the matched retracted nodes ------------------------------------------------------
con.execute("CREATE TABLE rnodes AS SELECT DISTINCT iid FROM rw_iid")
con.execute(f"""CREATE TABLE rdeg AS
   SELECT n.iid, coalesce(o.k, 0) AS out_deg, coalesce(i.k, 0) AS in_deg FROM rnodes n
   LEFT JOIN (SELECT citing_iid iid, count(*) k FROM read_parquet('{E}') WHERE citing_iid IN (SELECT iid FROM rnodes) GROUP BY 1) o USING (iid)
   LEFT JOIN (SELECT cited_iid iid, count(*) k FROM read_parquet('{E}') WHERE cited_iid IN (SELECT iid FROM rnodes) GROUP BY 1) i USING (iid)""")
run.log("retracted_nodes", one("SELECT count(*) FROM rdeg"))
run.log("retracted_nodes_out_deg_0", one("SELECT count(*) FROM rdeg WHERE out_deg = 0"))
run.log("retracted_nodes_in_deg_0", one("SELECT count(*) FROM rdeg WHERE in_deg = 0"))
run.log("retracted_nodes_isolated", one("SELECT count(*) FROM rdeg WHERE in_deg = 0 AND out_deg = 0"))
run.log("retracted_edges_out_in", q("SELECT sum(out_deg), sum(in_deg) FROM rdeg")[0])

# --- 5. Populations (sizes only) ---------------------------------------------------------------------------
# Biomedical node = has a PMID in Meta, or its DOI is a PubMed DOI.
con.execute("""CREATE TABLE bio AS SELECT DISTINCT iid FROM idm WHERE id_type = 'pmid'
               UNION SELECT DISTINCT i.iid FROM idm i JOIN (SELECT DISTINCT doi FROM pm WHERE doi IS NOT NULL) d
                     ON i.id_type = 'doi' AND i.id = d.doi""")
run.log("biomedical_nodes", one("SELECT count(*) FROM bio"))
run.log("biomedical_nodes_via_pmid_only_meta", one("SELECT count(DISTINCT iid) FROM idm WHERE id_type='pmid'"))
con.execute(f"""CREATE TABLE status AS
   SELECT r.iid, min(rw2.notice_date) AS first_notice FROM rw_iid r JOIN rw2 USING (key) GROUP BY 1""")
con.execute(f"""CREATE TABLE cand AS SELECT b.iid, p.pub_year FROM bio b JOIN read_parquet('{PUBS}') p USING (iid)
               WHERE p.pub_year BETWEEN 2010 AND 2023
               AND b.iid NOT IN (SELECT iid FROM status WHERE first_notice <= DATE '{T0}')""")
run.log("candidates_2010_2023", one("SELECT count(*) FROM cand"))
run.log("candidates_2015_2023", one("SELECT count(*) FROM cand WHERE pub_year >= 2015"))
con.execute(f"""CREATE TABLE cand_out AS SELECT c.iid, c.pub_year, count(e.cited_iid) AS refs FROM cand c
               LEFT JOIN read_parquet('{E}') e ON e.citing_iid = c.iid GROUP BY ALL""")
run.log("candidates_2015_2023_with_refs", one("SELECT count(*) FROM cand_out WHERE pub_year >= 2015 AND refs > 0"))
run.log("candidates_with_refs_by_year", q("SELECT pub_year, count(*), count(*) FILTER (refs > 0) FROM cand_out GROUP BY 1 ORDER BY 1"))
# Outcome label counts (base rate only; no scores exist yet)
run.log("positives_2015_2023", one(f"""SELECT count(*) FROM cand_out c JOIN status s USING (iid)
         WHERE c.pub_year >= 2015 AND s.first_notice > DATE '{T0}'"""))
run.log("positives_2015_2023_with_refs", one(f"""SELECT count(*) FROM cand_out c JOIN status s USING (iid)
         WHERE c.pub_year >= 2015 AND c.refs > 0 AND s.first_notice > DATE '{T0}'"""))
run.log("positives_2015_2023_paper_mill", one(f"""SELECT count(DISTINCT c.iid) FROM cand_out c JOIN status s USING (iid)
         JOIN rw_iid ri USING (iid) JOIN rw2 USING (key) WHERE c.pub_year >= 2015 AND s.first_notice > DATE '{T0}' AND rw2.paper_mill"""))
# Exposure prevalence among candidates (no outcome involved)
con.execute(f"""CREATE TABLE r_t0 AS SELECT iid FROM status WHERE first_notice <= DATE '{T0}'""")
run.log("candidates_2015_2023_citing_ge1_retracted_at_T0", one(f"""SELECT count(DISTINCT e.citing_iid) FROM read_parquet('{E}') e
         JOIN r_t0 r ON e.cited_iid = r.iid JOIN cand c ON c.iid = e.citing_iid WHERE c.pub_year >= 2015"""))
run.log("candidates_2015_2023_cited_by_ge1_retracted_at_T0", one(f"""SELECT count(DISTINCT e.cited_iid) FROM read_parquet('{E}') e
         JOIN r_t0 r ON e.citing_iid = r.iid JOIN cand c ON c.iid = e.cited_iid WHERE c.pub_year >= 2015"""))

for t in ["rw2", "rw_iid", "rdeg", "status"]:
    con.execute(f"COPY {t} TO '{W / (t + '_' + sys.argv[1] + '.parquet')}' (FORMAT parquet)")
run.log("saved_tables", ["rw2", "rw_iid", "rdeg", "status"])
run.finish()
