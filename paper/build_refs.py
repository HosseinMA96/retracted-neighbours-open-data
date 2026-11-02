"""Rebuild refs.bib from dois.txt and the BibTeX fetched by DOI content negotiation (bib_raw/<key>.bib).
To fetch a new entry: curl -sL -H "Accept: application/x-bibtex; charset=utf-8" https://doi.org/<doi> > bib_raw/<key>.bib
Fixes applied (logged in bib_verification.tsv): key renamed to ours; month macros dropped; '&' escaped;
mantel1959 completed by hand (Crossref record lacks authors and pages; checked against PubMed 13655060);
rittman2025rw typed as @misc (Crossref blog post); output converted to pure ASCII (LaTeX escapes);
ocmeta2024dump author made a corporate name (as in Paper C);
titles: proper nouns braced (PROPER list) so sn-basic keeps their capitals;
teixeira2025citation: compound surname braced so it sorts under T (BibTeX read "da" as a particle);
azoulay2015retractions: Krieger's given name added (NBER w18499 lists "Joshua L. Krieger").
usage: python build_refs.py
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
MANTEL = ("@article{mantel1959, author={Mantel, Nathan and Haenszel, William}, title={Statistical Aspects of the "
          "Analysis of Data From Retrospective Studies of Disease}, journal={JNCI: Journal of the National Cancer "
          "Institute}, volume={22}, number={4}, pages={719--748}, year={1959}, doi={10.1093/jnci/22.4.719}}")
out = []
for line in (HERE / "dois.txt").read_text().splitlines():
    key, doi = line.split("\t")
    b = (HERE / "bib_raw" / f"{key}.bib").read_text().strip()
    if not re.match(r"@[a-zA-Z]+\{", b):
        raise SystemExit(f"{key}: bib_raw is not BibTeX (failed fetch?)")
    b = re.sub(r"@([a-zA-Z]+)\{[^,]*,", lambda m: f"@{m.group(1)}{{{key},", b, count=1)
    b = re.sub(r",\s*month\s*=\s*[a-zA-Z]+\s*", "", b)
    b = re.sub(r"(?<!\\)&", r"\\&", b.replace("&amp;", "&"))
    if key == "mantel1959":
        b = MANTEL
    if key == "azoulay2015retractions":   # Crossref lacks Krieger's given name; NBER w18499 page: "Joshua L. Krieger"
        b = b.replace("and Krieger and", "and Krieger, Joshua L. and")
    if key == "ocmeta2024dump":   # DataCite gives "author = {, OpenCitations}" (empty surname): crashes sn-basic BibTeX
        b = re.sub(r"author = \{[\s\u200b]*, OpenCitations\}", "author = {{OpenCitations}}", b)   # raw has a zero-width space
    if key == "teixeira2025citation":   # protect the compound surname so BibTeX sorts it under T, not "Silva"
        b = b.replace("Teixeira da Silva, Jaime A.", "{Teixeira da Silva}, Jaime A.")
    if key == "rittman2025rw":
        b = re.sub(r"^@article", "@misc", b)[:-1] + ", howpublished={Crossref blog}}"
    out.append(b)
# Pure ASCII (Springer compiles with pdflatex): accents as LaTeX escapes, typographic marks as ASCII.
ASCII = {"\u00e1": "{\\'a}", "\u00c1": "{\\'A}", "\u00e9": "{\\'e}", "\u00ed": "{\\'i}", "\u00f3": "{\\'o}",
         "\u0151": "{\\H{o}}", "\u00fc": '{\\"u}', "\u2013": "--", "\u2014": "---", "\u2019": "'", "\u2018": "'",
         "\u2010": "-", "\u200b": "", "\u00a0": " "}
# Protect proper nouns in titles (author-year styles such as sn-basic lowercase titles).
PROPER = ["OpenCitations", "PubMed", "Web of Science", "Retraction Watch", "National Institutes of Health",
          "National Science Foundation", "NIH", "NSF", "Crossref", "DuckDB", "COCI", "Meta", "SaneCite", "Louvain",
          "Leiden", "Mantel-Haenszel", "Google Scholar", "Microsoft Academic", "Scopus", "Dimensions", "Nature",
          "Problematic Paper Screener", "Chest", "CSV", "API", "ROC", "DOI"]
def protect(entry):
    def fix(m):
        t = m.group(2)
        for w in sorted(PROPER, key=len, reverse=True):
            t = re.sub(r"(?<![{\\w])" + re.escape(w) + r"(?![}\\w])", "{" + w + "}", t)
        return m.group(1) + t + m.group(3)
    return re.sub(r"(\btitle\s*=\s*\{)(.*?)(\}\s*,)", fix, entry, count=1, flags=re.S)
out = [protect(b) for b in out]
text = "\n\n".join(out) + "\n"
for k, v in ASCII.items():
    text = text.replace(k, v)
bad = sorted({c for c in text if ord(c) > 127})
if bad:
    raise SystemExit(f"non-ASCII characters left in refs.bib: {bad} (add them to ASCII)")
(HERE / "refs.bib").write_text(text)
print(f"refs.bib: {len(out)} entries")
