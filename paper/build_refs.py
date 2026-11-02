"""Rebuild refs.bib from dois.txt and the BibTeX fetched by DOI content negotiation (bib_raw/<key>.bib).
To fetch a new entry: curl -sL -H "Accept: application/x-bibtex; charset=utf-8" https://doi.org/<doi> > bib_raw/<key>.bib
Fixes applied (logged in bib_verification.tsv): key renamed to ours; month macros dropped; '&' escaped;
mantel1959 completed by hand (Crossref record lacks authors and pages; checked against PubMed 13655060);
rittman2025rw typed as @misc (Crossref blog post);
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
    if key == "rittman2025rw":
        b = re.sub(r"^@article", "@misc", b)[:-1] + ", howpublished={Crossref blog}}"
    out.append(b)
(HERE / "refs.bib").write_text("\n\n".join(out) + "\n")
print(f"refs.bib: {len(out)} entries")
