# D12 label-quality checks: lab notebook

Protocol fixed before running (2026-11-01), in the docstring of `d12_check.py`: 300 DOI-keyed matched papers, seed 20261101; token-Jaccard of titles, classes ≥0.8 same, 0.5–0.8 check, <0.5 suspect; non-same rows written out for reading. Plus a profile of PubMed-flagged papers absent from Retraction Watch.

## d12_check_20261101_01 (299 s)
**(1) Match precision** (300 DOI-keyed matches; Meta title found for 292):
- Classes: same 270, check 21, suspect 9.
- Read all 30 non-same rows (`non_same_matches.csv`): the 21 "check" rows are all the same paper; the graph title carries a retraction prefix ("Notice of Retraction:", "RETRACTED ARTICLE:", "THIS ARTICLE HAS BEEN RETRACTED") or different casing/spacing. Of the 9 "suspect" rows, 8 have **no title in Meta** (cannot be judged) and 1 is a truncated title of the same paper ("Nirnayam").
- **Result: 0 wrong matches among the 292 judgeable (95% upper bound ≈ 1.0% by the rule of three: 3/292).**
**(2) PubMed-flagged papers absent from Retraction Watch:** 3,205 (3,156 with a DOI). Notice publication year: 2023 116, **2024 561, 2025 1,582, 2026 222**; before 2023: 284 in all. So 2,365 (74%) are 2024+ notices, i.e. recent retractions that the Retraction Watch copy has not (yet) recorded or recorded under another identifier. Top journals: Int Wound J 159, Eur Rev Med Pharmacol Sci 63, Oncol Res 62, Comput Intell Neurosci 52, J Int Med Res 47.
- Implication for D8: some post-T0 retractions are missing from the outcome labels (Retraction Watch is the single label source), which can only lower measured precision; state in Limitations.

## d12_check_20261101_02 (cited run): reproducibility fix
Sample order made deterministic (`ORDER BY key, iid`, stable sort). Results identical to `_01`: same 270 / 21 / 9, 292 with a Meta title, same PubMed-only profile.
