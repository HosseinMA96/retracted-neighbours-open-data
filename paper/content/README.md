# Central paper content (Paper D)
Single source of truth for the text; journal versions only change the wrapper (as in Paper C).
- `meta.tex`, `abstract.tex`, `intro.tex`, `related.tex`, `methods.tex`, `results.tex`, `discussion.tex`, `conclusions.tex`, `availability.tex`, `ai_use.tex`.
- Figures: `../figures/` (made by `experiments/d13_figures/d13_figures.py`); references: `../refs.bib` (rebuilt by `../build_refs.py` from `../dois.txt` and `../bib_raw/`; verified in `../bib_verification.tsv`).
- Cite with `\citep{}` / `\citet{}`. Numbers trace to `../../FINDINGS.md`. No first person except "to my knowledge" (single author).
- Build: `~/anaconda3/envs/tectonic-env/bin/tectonic -X compile main.tex` from `paper/`.
