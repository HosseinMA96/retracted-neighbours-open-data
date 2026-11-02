#!/usr/bin/env bash
# Build the Scientometrics upload package: submission/ (flat main.tex with all content inlined, refs.bib, main.bbl,
# figures, sn-jnl.cls, sn-basic.bst, main.pdf) and scientometrics_latex_source.zip. Springer compiles with pdflatex,
# so the package is pure ASCII and needs no fontspec. Re-run after any change to ../../content or ../../refs.bib.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; P="$(cd "$HERE/../.." && pwd)"; OUT="$HERE/submission"
TECTONIC="${TECTONIC:-$HOME/anaconda3/envs/tectonic-env/bin/tectonic}"
rm -rf "$OUT"; mkdir -p "$OUT"
python3 - "$HERE/main.tex" "$OUT/main.tex" <<'PY'
import re, sys, pathlib
src = pathlib.Path(sys.argv[1]); base = src.parent
def inline(text, cwd):
    def rep(m):
        f = (cwd / m.group(1)); f = f if f.suffix else f.with_suffix(".tex")
        return inline(f.read_text(), f.parent).rstrip("\n")
    return re.sub(r"\\input\{([^}]+)\}", rep, text)
t = inline(src.read_text(), base)
t = t.replace("\\graphicspath{{../../figures/}}", "\\graphicspath{{./}}").replace("\\bibliography{../../refs}", "\\bibliography{refs}")
t = t.replace("% Build: pdflatex + bibtex (Springer); locally tectonic -X compile main.tex. No fontspec: Springer compiles with pdflatex.",
              "% Build: pdflatex main; bibtex main; pdflatex main; pdflatex main")
assert "\\input{" not in t, "unresolved \\input"
bad = sorted({c for c in t if ord(c) > 127}); assert not bad, f"non-ASCII in main.tex: {bad}"
pathlib.Path(sys.argv[2]).write_text(t)
PY
cp "$P/refs.bib" "$HERE/sn-jnl.cls" "$HERE/sn-basic.bst" "$OUT/"
for f in fig1_dose fig2_mh fig3_event; do cp "$P/figures/$f.pdf" "$OUT/"; done
( cd "$OUT" && "$TECTONIC" -X compile --keep-intermediates main.tex >/dev/null 2>"$OUT/.build.err" ) || { cat "$OUT/.build.err"; exit 1; }
grep -q "panicked" "$OUT/.build.err" && { cat "$OUT/.build.err"; exit 1; }
rm -f "$OUT/.build.err" "$OUT/main.aux" "$OUT/main.blg" "$OUT/main.log" "$OUT/main.out"
test -s "$OUT/main.bbl" || { echo "main.bbl missing"; exit 1; }
( cd "$OUT" && rm -f ../scientometrics_latex_source.zip && zip -q -X ../scientometrics_latex_source.zip main.tex main.bbl refs.bib sn-jnl.cls sn-basic.bst fig1_dose.pdf fig2_mh.pdf fig3_event.pdf )
echo "package: $(unzip -l "$HERE/scientometrics_latex_source.zip" | tail -1 | awk '{print $2" files, "$1" bytes"}'); PDF: $(pdfinfo "$OUT/main.pdf" | awk '/Pages/{print $2}') pages"
