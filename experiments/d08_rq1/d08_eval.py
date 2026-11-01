"""D8b: evaluate the FROZEN scores against post-T0 retractions, exactly as PREREGISTRATION.md §5.
Aggregates only (no per-paper output).
usage: python d08_eval.py RUN_ID SCORES_RUN_ID MATCH_RUN_ID [n_boot]
"""
import json, sys, zlib
from multiprocessing import Pool
import duckdb, numpy as np, pandas as pd
from scipy.stats import norm
import statsmodels.api as sm
from common import Run, D_DATA, sha256

W = D_DATA / "work"; SR, M = sys.argv[2], sys.argv[3]
NB = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
SEED, END, KS = 20261101, "2026-10-30", [100, 1000, 10000]
SETT = {"main_T0": "2024-01-31", "sens_T0p": "2023-09-30", "train_Tm1": "2021-12-31"}
sdir = W / "d08" / SR
scores_run = json.loads((D_DATA.parent / f"experiments/d08_rq1/runs/{SR}/run.json").read_text())
run = Run(sys.argv[1], __file__, {"scores_run": SR, "match_run": M, "n_boot": NB, "seed": SEED, "end": END, "ks": KS})
for name in SETT:   # the frozen files must be unchanged
    f = sdir / f"scores_{name}.parquet"
    assert sha256(f) == scores_run["results"][name]["sha256"], f"{f} changed after freezing"
run.log("frozen_scores_verified", True)
con = duckdb.connect(); con.execute("SET threads=8; SET memory_limit='40GB'")
con.execute(f"""CREATE TABLE st AS SELECT ri.iid, min(r.notice_date) AS first_notice, bool_or(r.paper_mill) AS mill
   FROM read_parquet('{W / f'rw_iid_{M}.parquet'}') ri JOIN read_parquet('{W / f'rw2_{M}.parquet'}') r USING (key) GROUP BY 1""")

def load(name, upper):
    T = SETT[name]
    return con.execute(f"""SELECT s.*, (st.first_notice > DATE '{T}' AND st.first_notice <= DATE '{upper}') AS y,
        coalesce(st.mill, false) AND (st.first_notice > DATE '{T}' AND st.first_notice <= DATE '{upper}') AS y_mill
        FROM read_parquet('{sdir / f'scores_{name}.parquet'}') s LEFT JOIN st USING (iid) ORDER BY s.iid""").df().assign(
        y=lambda d: d.y.fillna(False).astype(bool), y_mill=lambda d: d.y_mill.fillna(False).astype(bool))

def wilson(k, n, z=1.96):
    if n == 0: return (None, None, None)
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (p, c - h, c + h)

def dose(d):
    bins = pd.cut(d.s1, [-1, 0, 1, 2, 4, np.inf], labels=["0", "1", "2", "3-4", "5+"])
    rows = []
    for b, g in d.groupby(bins, observed=True):
        p, lo, hi = wilson(int(g.y.sum()), len(g)); rows.append({"s1": str(b), "n": len(g), "pos": int(g.y.sum()), "rate": p, "lo": lo, "hi": hi})
    return rows

def rr(d, e):
    a, n1 = int(d.y[e].sum()), int(e.sum()); c, n0 = int(d.y[~e].sum()), int((~e).sum())
    r = (a / n1) / (c / n0); se = np.sqrt(1 / a - 1 / n1 + 1 / c - 1 / n0) if a and c else np.nan
    return {"exposed": n1, "exposed_pos": a, "unexposed": n0, "unexposed_pos": c, "rr": r,
            "lo": r * np.exp(-1.96 * se), "hi": r * np.exp(1.96 * se)}

def mh(d, e, y):
    t = pd.DataFrame({"j": d.journal_id.values, "yr": d.pub_year.values, "e": e.values, "y": y.values})
    g = t.groupby(["j", "yr"]).agg(n=("e", "size"), n1=("e", "sum"), pos=("y", "sum"))
    a = t[t.e & t.y].groupby(["j", "yr"]).size().reindex(g.index, fill_value=0)
    n1 = g.n1; n0 = g.n - g.n1; c = g.pos - a; b = n1 - a; dd = n0 - c; n = g.n.astype(float)
    inf = (n1 > 0) & (n0 > 0) & (g.pos > 0)
    a, b, c, dd, n = a[inf].astype(float), b[inf].astype(float), c[inf].astype(float), dd[inf].astype(float), n[inf]
    R, S = a * dd / n, b * c / n; P, Q = (a + dd) / n, (b + c) / n
    orr = R.sum() / S.sum()
    v = (P * R).sum() / (2 * R.sum() ** 2) + (P * S + Q * R).sum() / (2 * R.sum() * S.sum()) + (Q * S).sum() / (2 * S.sum() ** 2)
    se = np.sqrt(v)
    return {"or_mh": orr, "lo": orr * np.exp(-1.96 * se), "hi": orr * np.exp(1.96 * se), "strata_total": int(len(g)),
            "strata_informative": int(inf.sum()), "positives_in_informative": int((a + c).sum()),
            "exposed_positives_in_informative": int(a.sum())}

def features(d):
    X = pd.DataFrame({"logit_b": np.log(d.b / (1 - d.b)), "l1p_s1": np.log1p(d.s1), "l1p_s3": np.log1p(d.s3),
                      "s1_ge1": (d.s1 >= 1).astype(float)})
    age = d.age.clip(upper=8)
    for a in range(1, 9): X[f"age_{a}"] = (age == a).astype(float)   # age 0 = reference
    return X

def order(score, tie2, rng):
    u = rng.random(len(score))
    return np.lexsort((u, -tie2, -score))      # last key = primary

def _boot(args):
    y_sorted, seeds = args
    out = []
    for s in seeds:
        r = np.random.default_rng(s); w = r.poisson(1.0, len(y_sorted)).astype(np.int32)
        cw = np.cumsum(w, dtype=np.int64); cy = np.cumsum(w * y_sorted, dtype=np.int64)
        base = cy[-1] / cw[-1]; m = {}
        for k in KS:
            i = min(np.searchsorted(cw, k), len(cw) - 1); m[f"prec@{k}"] = cy[i] / cw[i]; m[f"lift@{k}"] = m[f"prec@{k}"] / base
        i = min(np.searchsorted(cw, 10000), len(cw) - 1); m["recall@10000"] = cy[i] / cy[-1]
        m["ap"] = float((w * y_sorted * (cy / np.maximum(cw, 1))).sum() / cy[-1])
        out.append(m)
    return out

def screen(y_sorted, label, pool):
    n, pos = len(y_sorted), int(y_sorted.sum()); cy = np.cumsum(y_sorted); base = pos / n
    point = {f"prec@{k}": cy[k - 1] / k for k in KS}
    point.update({f"lift@{k}": point[f"prec@{k}"] / base for k in KS}); point["recall@10000"] = cy[9999] / pos
    point["ap"] = float((y_sorted * (cy / np.arange(1, n + 1))).sum() / pos)
    seeds = np.random.SeedSequence([SEED, zlib.crc32(label.encode())]).generate_state(NB)
    chunks = [(y_sorted, seeds[i::8]) for i in range(8)]
    bs = pd.DataFrame([m for c in pool.map(_boot, chunks) for m in c])
    return {"base_rate": base, **{k: {"point": v, "lo": float(bs[k].quantile(.025)), "hi": float(bs[k].quantile(.975))} for k, v in point.items()}}

def analyse(d, tag, model, pool):
    res = {"n": len(d), "positives": int(d.y.sum()), "positives_mill": int(d.y_mill.sum())}
    res["dose_s1"] = dose(d)
    res["rr"] = {"s1_ge1": rr(d, d.s1 >= 1), "s3_ge1": rr(d, d.s3 >= 1), "s4_ge1": rr(d, d.s4 >= 1)}
    res["mh"] = {}
    for en, e in {"s1_ge1": d.s1 >= 1, "s3_ge1": d.s3 >= 1}.items():
        for yn, yy in {"all": d.y, "mill": d.y_mill, "nonmill": d.y & ~d.y_mill}.items():
            res["mh"][f"{en}|{yn}"] = mh(d, e, yy)
    rng = np.random.default_rng(SEED); y = d.y.values.astype(np.int64)
    p = model.predict_proba(features(d).values)[:, 1]
    res["screen"] = {
        "s1": screen(y[order(d.s1.values.astype(float), d.s2.values, rng)], tag + "s1", pool),
        "journal_b": screen(y[order(d.b.values, np.zeros(len(d)), rng)], tag + "b", pool),
        "combined": screen(y[order(p, np.zeros(len(d)), rng)], tag + "comb", pool)}
    run.log(tag, res)
    return res

# --- combined model: fit on the training window only ---------------------------------------------------
tr = load("train_Tm1", SETT["main_T0"])
Xtr = sm.add_constant(features(tr), has_constant="add")
fit = sm.Logit(tr.y.values.astype(float), Xtr.values).fit(method="newton", maxiter=100, tol=1e-10, disp=False)
assert fit.mle_retvals["converged"], "logit did not converge"
class Model:   # same interface as before: predict_proba(X)[:, 1]
    def predict_proba(self, X):
        p = fit.predict(sm.add_constant(X, has_constant="add")); return np.column_stack([1 - p, p])
model = Model()
run.log("train", {"n": len(tr), "positives": int(tr.y.sum()), "converged": True, "iterations": int(fit.mle_retvals["iterations"]),
                  "coef": dict(zip(Xtr.columns, np.round(fit.params, 4).tolist())),
                  "se": dict(zip(Xtr.columns, np.round(fit.bse, 4).tolist())), "llf": float(fit.llf)})
del tr, Xtr

with Pool(8) as pool:
    main = load("main_T0", END)
    analyse(main, "main_T0", model, pool)
    analyse(main[main.pub_year <= 2022].reset_index(drop=True), "sens_a_pub2015_2022", model, pool)
    analyse(main[~main.dup_doi].reset_index(drop=True), "sens_b_no_dup_doi", model, pool)
    # 5.4 checks: exposure prevalence by publication year (no outcome); PubMed notice year of positives
    run.log("exposure_by_year", main.groupby("pub_year").agg(n=("s1", "size"), s1_ge1=("s1", lambda s: int((s >= 1).sum()))).reset_index().to_dict("records"))
    pos = main.loc[main.y, ["iid"]]; con.register("pos", pos)
    run.log("positives_with_pubmed_notice_year", con.execute(f"""
        WITH pm AS (SELECT pmid, year, cc_reftype, cc_pmid FROM read_parquet('{W / 'pubmed26.parquet'}')),
        ids AS (SELECT DISTINCT p.iid, CAST(i.id AS BIGINT) pmid FROM pos p JOIN read_parquet('{W / 'idmap.parquet'}') i
                ON i.iid = p.iid AND i.id_type = 'pmid'),
        notes AS (SELECT ids.iid, unnest(list_filter(list_zip(pm.cc_reftype, pm.cc_pmid), x -> x[1] = 'RetractionIn')) z
                  FROM ids JOIN pm USING (pmid))
        SELECT n2.year AS notice_pub_year, count(DISTINCT notes.iid) FROM notes JOIN pm n2 ON n2.pmid = notes.z[2]
        GROUP BY 1 ORDER BY 1""").fetchall())
    del main
    analyse(load("sens_T0p", END), "sens_c_T0p", model, pool)
run.finish()
