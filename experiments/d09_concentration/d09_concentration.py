"""D9 (RQ2): are retracted papers concentrated in citation communities beyond what matched controls show?
Pairs: every retracted biomedical paper (any notice date) with a journal, matched to one non-retracted paper of the
same journal and publication year (deterministic: lowest hash(iid, 20261101) within journal x year). Subgraph: pairs + their 1-hop neighbours; induced edges, undirected.
Communities: Leiden (modularity, leidenalg, seeds 1 and 2). Statistic: concentration C = sum_c share_c^2 of an arm's
nodes over communities (probability that two random members share a community); ratio C_ret / C_ctrl.
Null: swap labels within each pair with probability 1/2 (keeps journal and year exactly), 1,000 permutations.
Aggregates only. usage: python d09_concentration.py RUN_ID MATCH_RUN_ID
"""
import sys, duckdb, numpy as np, pandas as pd, igraph as ig, leidenalg as la
from concurrent.futures import ProcessPoolExecutor
from common import Run, C_WORK, D_DATA

W = D_DATA / "work"; M = sys.argv[2]; SEED = 20261101; NPERM = 1000   # SEED: hash seed for deterministic control choice
run = Run(sys.argv[1], __file__, {"match_run": M, "nperm": NPERM, "leiden": "ModularityVertexPartition, seeds 1,2 in parallel processes, n_iterations=2 (leidenalg default)"})
con = duckdb.connect(); con.execute(f"SET threads=8; SET memory_limit='48GB'; SET temp_directory='{W / 'tmp'}'")
q = lambda s: con.execute(s).fetchall()
E = f"read_parquet('{C_WORK / 'edges.parquet'}')"
con.execute(f"CREATE TABLE idm AS SELECT iid, id_type, id FROM read_parquet('{W / 'idmap.parquet'}') WHERE iid IS NOT NULL")
con.execute(f"""CREATE TABLE bio AS SELECT DISTINCT iid FROM idm WHERE id_type='pmid'
   UNION SELECT DISTINCT i.iid FROM idm i JOIN (SELECT DISTINCT doi FROM read_parquet('{W / 'pubmed26.parquet'}') WHERE doi IS NOT NULL) d
   ON i.id_type='doi' AND i.id=d.doi""")
con.execute(f"""CREATE TABLE node AS SELECT b.iid, p.pub_year, j.journal_id FROM bio b JOIN read_parquet('{C_WORK / 'pubs_slim.parquet'}') p USING (iid)
   JOIN read_parquet('{C_WORK / 'pubs_j.parquet'}') j USING (iid)""")
con.execute(f"""CREATE TABLE ret AS SELECT ri.iid, bool_or(r.paper_mill) mill
   FROM read_parquet('{W / f'rw_iid_{M}.parquet'}') ri JOIN read_parquet('{W / f'rw2_{M}.parquet'}') r USING (key) GROUP BY 1""")
con.execute("CREATE TABLE tr AS SELECT n.*, ret.mill FROM node n JOIN ret USING (iid)")
con.execute("""CREATE TABLE pool AS SELECT iid, pub_year, journal_id, hash(iid, 20261101) u FROM node
               WHERE (journal_id, pub_year) IN (SELECT journal_id, pub_year FROM tr) AND iid NOT IN (SELECT iid FROM ret)""")
con.execute("""CREATE TABLE pairs AS SELECT t.iid r, p.iid c, t.mill FROM
   (SELECT *, row_number() OVER (PARTITION BY journal_id, pub_year ORDER BY iid) rk FROM tr) t
   JOIN (SELECT *, row_number() OVER (PARTITION BY journal_id, pub_year ORDER BY u, iid) rk FROM pool) p USING (journal_id, pub_year, rk)""")
run.log("retracted_with_journal", q("SELECT count(*) FROM tr")[0][0])
run.log("pairs", q("SELECT count(*) FROM pairs")[0][0]); run.log("pairs_mill", q("SELECT count(*) FROM pairs WHERE mill")[0][0])
con.execute("CREATE TABLE seed AS SELECT r iid FROM pairs UNION SELECT c FROM pairs")
con.execute(f"""CREATE TABLE vs AS SELECT iid FROM seed UNION
   SELECT e.cited_iid FROM {E} e JOIN seed s ON e.citing_iid = s.iid UNION
   SELECT e.citing_iid FROM {E} e JOIN seed s ON e.cited_iid = s.iid""")
con.execute(f"""CREATE TABLE es AS SELECT e.citing_iid a, e.cited_iid b FROM {E} e
   SEMI JOIN vs v1 ON e.citing_iid = v1.iid SEMI JOIN vs v2 ON e.cited_iid = v2.iid""")
nv, ne = q("SELECT count(*) FROM vs")[0][0], q("SELECT count(*) FROM es")[0][0]
run.log("subgraph", {"nodes": nv, "edges_induced": ne})
ids = con.execute("SELECT iid FROM vs ORDER BY iid").df().iid.values
idx = pd.Series(np.arange(len(ids)), index=ids)
ed = con.execute("SELECT a, b FROM es ORDER BY a, b").df()
g = ig.Graph(n=len(ids), edges=np.column_stack([idx[ed.a].values, idx[ed.b].values]), directed=False)
del ed; g.simplify()
pairs = con.execute("SELECT r, c, mill FROM pairs ORDER BY r").df()
ri, ci, mill = idx[pairs.r].values, idx[pairs.c].values, pairs.mill.values

def conc(memb, nodes):
    _, cnt = np.unique(memb[nodes], return_counts=True); s = cnt / cnt.sum(); return float((s * s).sum())

def fit(seed):
    part = la.find_partition(g, la.ModularityVertexPartition, seed=seed, n_iterations=2)
    return np.array(part.membership), float(part.modularity)

with ProcessPoolExecutor(2) as ex:      # forked workers share the graph copy-on-write
    fits = dict(zip((1, 2), ex.map(fit, (1, 2))))
memb1, memb2 = fits[1][0], fits[2][0]
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
run.log("seed_agreement", {"ari": float(adjusted_rand_score(memb1, memb2)), "nmi": float(normalized_mutual_info_score(memb1, memb2))})
np.save(W / f"d09_membership_{sys.argv[1]}_seed1.npy", memb1); np.save(W / f"d09_membership_{sys.argv[1]}_seed2.npy", memb2)
np.save(W / f"d09_node_iids_{sys.argv[1]}.npy", ids)
for seed in (1, 2):
    memb, modularity = fits[seed]; sizes = np.bincount(memb)
    res = {"communities": int(memb.max() + 1), "modularity": modularity,
           "largest_community_share": float(sizes.max() / len(memb))}
    rng = np.random.default_rng(20261101 + seed)
    for name, sel in {"all": np.ones(len(ri), bool), "mill": mill, "nonmill": ~mill}.items():
        r_, c_ = ri[sel], ci[sel]
        obs = conc(memb, r_) / conc(memb, c_)
        null = np.empty(NPERM)
        for k in range(NPERM):
            sw = rng.random(len(r_)) < 0.5
            null[k] = conc(memb, np.where(sw, c_, r_)) / conc(memb, np.where(sw, r_, c_))
        res[name] = {"pairs": int(sel.sum()), "C_ret": conc(memb, r_), "C_ctrl": conc(memb, c_), "ratio": obs,
                     "null_mean": float(null.mean()), "null_q975": float(np.quantile(null, .975)),
                     "p_perm": float((1 + (null >= obs).sum()) / (1 + NPERM))}
        # same-community rate for pairs of retracted papers in the same journal is excluded by design? report enrichment:
    # enrichment of the top communities by retracted count
    rc = np.bincount(memb[ri], minlength=len(sizes)); cc = np.bincount(memb[ci], minlength=len(sizes))
    top = np.argsort(-rc)[:20]
    res["top20_by_retracted"] = [{"size": int(sizes[t]), "retracted": int(rc[t]), "controls": int(cc[t])} for t in top]
    res["share_of_retracted_in_top20"] = float(rc[top].sum() / len(ri)); res["share_of_controls_in_top20_ret"] = float(cc[top].sum() / len(ci))
    run.log(f"leiden_seed{seed}", res)
run.finish()
