"""D15 (POST HOC, review round 1): is the neighbourhood signal explained by reference-list length? Are high-S1
papers reviews? Uses the FROZEN scores of d08_scores (hashes verified) and the same labels as d08_eval.
Not pre-specified; reported as post hoc. Aggregates only.
(a) Mantel-Haenszel OR of S1>=1 with strata journal x pub_year x decile of d(p) (reference count).
(b) The share version S2 = S1/d(p): positive rate by S2 bin; MH ORs for S2 bins vs S2 = 0 (same strata as (a)).
(c) Reviews: PubMed publication types Review (D016454), Systematic Review (D000078182), Meta-Analysis (D017418).
    Share of reviews by S1 level; positive rate by S1 level for reviews and non-reviews; MH (a) without reviews.
usage: python d15_lenadj.py RUN_ID SCORES_RUN_ID MATCH_RUN_ID
"""
import json, sys
import duckdb, numpy as np, pandas as pd
from common import Run, D_DATA, sha256

W = D_DATA / "work"; SR, M = sys.argv[2], sys.argv[3]
SETT = {"main_T0": "2024-01-31", "sens_c_T0p": "2023-09-30"}; FILE = {"main_T0": "main_T0", "sens_c_T0p": "sens_T0p"}
END = "2026-10-30"; REVIEW = ["D016454", "D000078182", "D017418"]
sdir = W / "d08" / SR
frozen = json.loads((D_DATA.parent / f"experiments/d08_rq1/runs/{SR}/run.json").read_text())["results"]
run = Run(sys.argv[1], __file__, {"post_hoc": True, "scores_run": SR, "match_run": M, "review_types": REVIEW,
                                   "deciles_of": "out_deg (reference count) over the setting's candidates"})
for k, f in FILE.items():
    assert sha256(sdir / f"scores_{f}.parquet") == frozen[f]["sha256"], f"{f} changed after freezing"
run.log("frozen_scores_verified", True)
con = duckdb.connect(); con.execute("SET threads=8; SET memory_limit='40GB'")
con.execute(f"""CREATE TABLE st AS SELECT ri.iid, min(r.notice_date) AS first_notice, bool_or(r.paper_mill) AS mill
   FROM read_parquet('{W / f'rw_iid_{M}.parquet'}') ri JOIN read_parquet('{W / f'rw2_{M}.parquet'}') r USING (key) GROUP BY 1""")
# review flag per graph node: any linked PubMed record (via Meta PMID or DOI) with a review-type publication type
con.execute(f"""CREATE TABLE rev AS SELECT iid, bool_or(is_rev) AS review FROM (
   SELECT i.iid, list_has_any(p.pub_type_ui, {REVIEW}) AS is_rev FROM read_parquet('{W / 'idmap.parquet'}') i
   JOIN read_parquet('{W / 'pubmed26.parquet'}') p ON i.id_type='pmid' AND CAST(i.id AS BIGINT) = p.pmid WHERE i.iid IS NOT NULL
   UNION ALL
   SELECT i.iid, list_has_any(p.pub_type_ui, {REVIEW}) FROM read_parquet('{W / 'idmap.parquet'}') i
   JOIN read_parquet('{W / 'pubmed26.parquet'}') p ON i.id_type='doi' AND i.id = p.doi WHERE i.iid IS NOT NULL) GROUP BY 1""")

def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [p, c - h, c + h]

def mh(t, e, y, strata):
    g = pd.DataFrame({"s": strata, "e": e, "y": y}).groupby("s").agg(n=("e", "size"), n1=("e", "sum"), pos=("y", "sum"))
    a = pd.Series(y & e).groupby(strata).sum().reindex(g.index, fill_value=0)
    n0 = g.n - g.n1; c = g.pos - a; b = g.n1 - a; d = n0 - c; inf = (g.n1 > 0) & (n0 > 0) & (g.pos > 0)
    a, b, c, d, n = (x[inf].astype(float) for x in (a, b, c, d, g.n))
    R, S, P, Q = a * d / n, b * c / n, (a + d) / n, (b + c) / n
    o = R.sum() / S.sum()
    v = (P * R).sum() / (2 * R.sum() ** 2) + (P * S + Q * R).sum() / (2 * R.sum() * S.sum()) + (Q * S).sum() / (2 * S.sum() ** 2)
    return {"or": float(o), "lo": float(o * np.exp(-1.96 * v ** .5)), "hi": float(o * np.exp(1.96 * v ** .5)),
            "strata_informative": int(inf.sum()), "exposed_positives": int(a.sum()), "positives": int((a + c).sum())}

for tag, T in SETT.items():
    d = con.execute(f"""SELECT s.iid, s.pub_year, s.journal_id, s.out_deg, s.s1, s.s2,
          (st.first_notice > DATE '{T}' AND st.first_notice <= DATE '{END}') AS y,
          coalesce(st.mill, false) AS mill, coalesce(rev.review, false) AS review
        FROM read_parquet('{sdir / f'scores_{FILE[tag]}.parquet'}') s LEFT JOIN st USING (iid) LEFT JOIN rev USING (iid)
        ORDER BY s.iid""").df()
    d["y"] = d.y.fillna(False).astype(bool); d["ym"] = d.y & d.mill
    d["dec"] = pd.qcut(d.out_deg.rank(method="first"), 10, labels=False)
    dec_edges = d.groupby("dec").out_deg.agg(["min", "max"]).reset_index().to_dict("records")
    s_jy = d.journal_id.astype(str) + "|" + d.pub_year.astype(str)
    s_jyd = s_jy + "|" + d.dec.astype(str)
    e1 = (d.s1 >= 1).values
    res = {"n": len(d), "positives": int(d.y.sum()), "out_deg_deciles": dec_edges,
           "out_deg_median_exposed_vs_not": [float(d.out_deg[e1].median()), float(d.out_deg[~e1].median())],
           "mh_journal_year": mh(d, e1, d.y.values, s_jy.values),
           "mh_journal_year_refdecile": mh(d, e1, d.y.values, s_jyd.values),
           "mh_journal_year_refdecile_mill": mh(d, e1, d.ym.values, s_jyd.values),
           "mh_journal_year_refdecile_nonmill": mh(d, e1, (d.y & ~d.mill).values, s_jyd.values)}
    # (b) share version
    bins = pd.cut(d.s2, [-1, 0, 0.01, 0.02, 0.05, 1.0], labels=["0", "(0,1%]", "(1%,2%]", "(2%,5%]", ">5%"])
    res["rate_by_s2"] = [{"s2": str(b), "n": int(len(g)), "pos": int(g.y.sum()), "rate_ci": wilson(int(g.y.sum()), len(g))}
                         for b, g in d.groupby(bins, observed=True)]
    res["mh_s2_bins_vs_0_journal_year_refdecile"] = {}
    for b in ["(0,1%]", "(1%,2%]", "(2%,5%]", ">5%"]:
        keep = ((bins == "0") | (bins == b)).values
        res["mh_s2_bins_vs_0_journal_year_refdecile"][b] = mh(d[keep], (bins[keep] == b).values, d.y.values[keep], s_jyd.values[keep])
    # (c) reviews
    lvl = pd.cut(d.s1, [-1, 0, 1, 2, 4, np.inf], labels=["0", "1", "2", "3-4", "5+"])
    res["reviews_total"] = int(d.review.sum())
    res["by_s1_level"] = []
    for b, g in d.groupby(lvl, observed=True):
        r, nr = g[g.review], g[~g.review]
        res["by_s1_level"].append({"s1": str(b), "n": int(len(g)), "review_share": float(g.review.mean()),
            "rate_reviews": wilson(int(r.y.sum()), len(r)) + [int(r.y.sum()), int(len(r))] if len(r) else None,
            "rate_nonreviews": wilson(int(nr.y.sum()), len(nr)) + [int(nr.y.sum()), int(len(nr))]})
    nr = ~d.review.values
    res["mh_journal_year_refdecile_nonreviews"] = mh(d[nr], e1[nr], d.y.values[nr], s_jyd.values[nr])
    run.log(tag, res)
run.finish()
