# D9 RQ2 (community concentration): lab notebook

Design in the docstring of `d09_concentration.py`. Descriptive; not pre-registered. Journal grouping is not used as an alternative grouping, because the pairs are matched on journal.

## d09_conc_20261101_01: STOPPED after 30 min (no community result computed)
Pairs 27,567 (5,394 paper-mill) from 28,859 retracted biomedical papers with a journal; subgraph 2,720,102 nodes, 57,402,166 induced edges. Leiden with `n_iterations=-1` (until convergence) was still in its first fit after 37 CPU-minutes; stopped to save time.

## d09_conc_20261101_02
Change: `n_iterations=2` (leidenalg default), seeds 1 and 2 fitted in parallel; seed agreement (ARI, NMI) logged; memberships saved on the VM (`~/d/data/work/d09_membership_*`) so they can go into the dataset.

## d09_conc_20261101_02 (574 s): results
- Leiden (modularity, 2 iterations): seed 1: 216 communities, modularity 0.659, largest community 9.8% of nodes; seed 2: 225, 0.659, 9.8%. **Seed agreement ARI 0.50, NMI 0.60**: the coarse partition is not stable in detail, so both seeds are reported.
- Concentration ratio C_ret / C_ctrl (permutation null swaps labels within pairs; 1,000 permutations; null mean ≈1.000):
  | | seed 1 | seed 2 |
  |---|---|---|
  | all (27,567 pairs) | **1.21** (null 97.5% 1.018; p = 0.001) | **1.08** (1.012; p = 0.001) |
  | paper mill (5,394) | **1.71** (1.060; p = 0.001) | **1.54** (1.046; p = 0.001) |
  | other (22,173) | 1.11 (1.018; p = 0.001) | 1.01 (1.012; p = 0.010) |
- p = 0.001 is the smallest possible value with 1,000 permutations.
- Reading: beyond what their journal and year imply, retracted papers sit together in citation communities, strongly for paper-mill retractions and weakly or not at all for other retractions. Effect sizes depend on the partition (seed).
- Memberships saved on the VM: `~/d/data/work/d09_membership_d09_conc_20261101_02_seed{1,2}.npy`, node order `d09_node_iids_d09_conc_20261101_02.npy`.

## d09_conc_20261101_03 (cited run): reproducibility fix
Reason: `_02` drew controls with DuckDB `setseed` + `random()`, which is not reproducible under multi-threading, and passed an unordered edge list to igraph. `_03` picks the control with the lowest `hash(iid, 20261101)` within journal × year and sorts edges by (citing, cited).
- Pairs 27,567 (5,394 paper-mill), as before. Subgraph 2,698,556 nodes, 57,223,086 edges (other controls → slightly different neighbourhood).
- Leiden: seed 1: 197 communities, modularity 0.651, largest 9.0%; seed 2: 200, 0.657, 9.0%; agreement ARI 0.41, NMI 0.57.
- Concentration ratio (seed 1 / seed 2; all p = 0.001, null 97.5% quantiles 1.012–1.056): **all 1.15 / 1.11; paper-mill 1.68 / 1.52; other 1.06 / 1.05.**
- Same reading as `_02`: clear excess for paper-mill retractions, small for others.
