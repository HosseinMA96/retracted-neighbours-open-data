"""D15b (POST HOC, review round 2): screening precision of the S1 ranking with reviews set aside.
Frozen scores (hashes verified); same ranking rule as d08_eval (S1 desc, then S2 desc, then a seeded random
tie-break after sorting rows by node ID); reviews = PubMed Review, Systematic Review or Meta-Analysis.
Precision@k with Wilson 95% intervals; base rate and lift. Aggregates only.
usage: python d15_screen_noreview.py RUN_ID SCORES_RUN_ID MATCH_RUN_ID
"""
import json, sys
import duckdb, numpy as np
from common import Run, D_DATA, sha256

W = D_DATA / "work"; SR, M = sys.argv[2], sys.argv[3]; SEED = 20261101; KS = [100, 1000, 10000]
SETT = {"main_T0": ("2024-01-31", "main_T0"), "sens_c_T0p": ("2023-09-30", "sens_T0p")}
END = "2026-10-30"; REVIEW = ["D016454", "D000078182", "D017418"]
sdir = W / "d08" / SR
frozen = json.loads((D_DATA.parent / f"experiments/d08_rq1/runs/{SR}/run.json").read_text())["results"]
run = Run(sys.argv[1], __file__, {"post_hoc": True, "scores_run": SR, "match_run": M, "seed": SEED, "ks": KS, "review_types": REVIEW})
for _, f in SETT.values():
    assert sha256(sdir / f"scores_{f}.parquet") == frozen[f]["sha256"], f"{f} changed after freezing"
run.log("frozen_scores_verified", True)
con = duckdb.connect(); con.execute("SET threads=8; SET memory_limit='40GB'")
con.execute(f"""CREATE TABLE st AS SELECT ri.iid, min(r.notice_date) AS first_notice
   FROM read_parquet('{W / f'rw_iid_{M}.parquet'}') ri JOIN read_parquet('{W / f'rw2_{M}.parquet'}') r USING (key) GROUP BY 1""")
con.execute(f"""CREATE TABLE rev AS SELECT iid, bool_or(is_rev) AS review FROM (
   SELECT i.iid, list_has_any(p.pub_type_ui, {REVIEW}) AS is_rev FROM read_parquet('{W / 'idmap.parquet'}') i
   JOIN read_parquet('{W / 'pubmed26.parquet'}') p ON i.id_type='pmid' AND CAST(i.id AS BIGINT) = p.pmid WHERE i.iid IS NOT NULL
   UNION ALL
   SELECT i.iid, list_has_any(p.pub_type_ui, {REVIEW}) FROM read_parquet('{W / 'idmap.parquet'}') i
   JOIN read_parquet('{W / 'pubmed26.parquet'}') p ON i.id_type='doi' AND i.id = p.doi WHERE i.iid IS NOT NULL) GROUP BY 1""")

def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [p, c - h, c + h]

def screen(s1, s2, y):
    u = np.random.default_rng(SEED).random(len(s1))
    o = np.lexsort((u, -s2, -s1)); ys = y[o]; base = y.mean(); cy = np.cumsum(ys)
    out = {"n": int(len(y)), "positives": int(y.sum()), "base_rate": float(base)}
    for k in KS:
        p, lo, hi = wilson(int(cy[k - 1]), k)
        out[f"@{k}"] = {"hits": int(cy[k - 1]), "precision": p, "lo": lo, "hi": hi, "lift": p / base}
    return out

for tag, (T, f) in SETT.items():
    d = con.execute(f"""SELECT s.iid, s.s1, s.s2, coalesce(rev.review, false) AS review,
          coalesce(st.first_notice > DATE '{T}' AND st.first_notice <= DATE '{END}', false) AS y
        FROM read_parquet('{sdir / f'scores_{f}.parquet'}') s LEFT JOIN st USING (iid) LEFT JOIN rev USING (iid)
        ORDER BY s.iid""").df()
    s1, s2, y, rv = d.s1.values.astype(float), d.s2.values.astype(float), d.y.values.astype(np.int64), d.review.values
    res = {"all_candidates": screen(s1, s2, y), "reviews_excluded": screen(s1[~rv], s2[~rv], y[~rv])}
    run.log(tag, res)
run.finish()
