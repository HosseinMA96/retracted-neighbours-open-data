# Central paper content (Paper D)
Single source of truth for the text; journal versions only change the wrapper (as in Paper C).
- `meta.tex`, `abstract.tex`, `intro.tex`, `related.tex`, `methods.tex`, `results.tex`, `discussion.tex`, `conclusions.tex`, `availability.tex`, `ai_use.tex`.
- Figures: `../figures/` (made by `experiments/d13_figures/d13_figures.py`); references: `../refs.bib` (rebuilt by `../build_refs.py` from `../dois.txt` and `../bib_raw/`; verified in `../bib_verification.tsv`).
- Cite with `\citep{}` / `\citet{}`. Numbers trace to `../../FINDINGS.md`. No first person except "to my knowledge" (single author).
- Builds: central `main.tex` (`tectonic -X compile main.tex` from `paper/`); Scientometrics `journals/scientometrics/main.tex` (Springer Nature sn-jnl, author-year). Upload package: `journals/scientometrics/build_submission.sh`.
- Text rules: no first person (single author; "the author"); refs.bib must stay pure ASCII (`build_refs.py` enforces it).
