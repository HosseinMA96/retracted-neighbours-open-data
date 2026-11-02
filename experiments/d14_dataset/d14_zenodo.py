"""D14b: create a Zenodo DRAFT for the release dataset (never publishes). Reserves a DOI, uploads the files, checks
Zenodo's MD5 against the local files, and records the draft id, reserved DOI and links in the run folder.
The access token is read from ~/.zenodo_token (mode 600); it is never printed or stored in the run record.
usage: python d14_zenodo.py RUN_ID RELEASE_RUN_ID
"""
import hashlib, json, sys
from pathlib import Path
import requests
from common import Run, D_DATA

API = "https://zenodo.org/api"
REL = D_DATA / "release" / sys.argv[2]
FILES = ["README.md", "retracted_papers.csv.gz", "citation_edges.csv.gz", "communities.csv.gz", "SHA256SUMS"]
TOKEN = Path.home().joinpath(".zenodo_token").read_text().strip()
H = {"Authorization": f"Bearer {TOKEN}"}
run = Run(sys.argv[1], __file__, {"api": API, "release": str(REL), "files": FILES, "publish": False})

DESCRIPTION = """
<p>Retraction labels and open citation links for the paper <em>Do links to retracted papers predict future retractions?
An out-of-sample test on the open biomedical citation graph</em> (H. Mohasel Arjomandi, submitted).</p>
<p><strong>Files</strong></p>
<ul>
<li><code>retracted_papers.csv.gz</code> (62,735 rows): every paper with a retraction in the Retraction Watch database
(copy of 30 October 2026, repository commit a98cc7e): DOI, PMID, date of the first retraction notice, publication year,
paper-mill flag, Retraction Watch reasons and article type, the matching OpenCitations OMIDs, and whether the paper is in the
January 2024 OpenCitations graph (52,254 are).</li>
<li><code>citation_edges.csv.gz</code> (2,259,192 rows): every citation in the OpenCitations snapshot of January 2024 in which
the citing or the cited paper is retracted, with OMID, DOI, PMID and publication year at both ends.</li>
<li><code>communities.csv.gz</code> (2,698,556 rows): Leiden community memberships (two seeds) for the subgraph used in the
paper's concentration analysis.</li>
<li><code>README.md</code> and <code>SHA256SUMS</code>.</li>
</ul>
<p><strong>Time split.</strong> Retraction dates let users choose any time point T: papers retracted by T are known, later ones
are outcomes. The graph is essentially complete to about September 2023.</p>
<p><strong>Not included, by design.</strong> No author names, titles or notes, and no score or ranking of non-retracted papers.
A retraction is a public editorial label and does not by itself imply misconduct.</p>
<p><strong>Sources.</strong> OpenCitations (parsed snapshot, Illinois Data Bank, doi:10.13012/B2IDB-5216575_V1, CC BY 4.0);
OpenCitations Meta (doi:10.6084/m9.figshare.21747461.v7, CC0); Retraction Watch database distributed by Crossref, CC0 per
Crossref's licence table (https://www.crossref.org/documentation/retrieve-metadata/), which permits redistribution
(please cite the source); PubMed identifiers courtesy of the U.S. National Library of Medicine (may not reflect the latest NLM data).</p>
<p>Code, pre-registration and run records: https://github.com/HosseinMA96/retracted-neighbours-open-data</p>
"""
META = {"metadata": {
    "upload_type": "dataset",
    "title": "Retracted papers and their open citation neighbourhoods: Retraction Watch labels linked to the OpenCitations graph (January 2024)",
    "creators": [{"name": "Mohasel Arjomandi, Hossein", "affiliation": "Microsoft"}],
    "description": DESCRIPTION.strip(),
    "access_right": "open",
    "license": "cc-by-4.0",
    "keywords": ["retraction", "research integrity", "citation network", "OpenCitations", "Retraction Watch",
                 "paper mills", "PubMed"],
    "version": "1.0",
    "language": "eng",
    "related_identifiers": [
        {"identifier": "https://github.com/HosseinMA96/retracted-neighbours-open-data", "relation": "isSupplementTo", "scheme": "url"},
        {"identifier": "10.13012/B2IDB-5216575_V1", "relation": "isDerivedFrom", "scheme": "doi"},
        {"identifier": "10.6084/m9.figshare.21747461.v7", "relation": "isDerivedFrom", "scheme": "doi"}],
    "notes": "Derived from public sources; see README.md for definitions. Retraction labels follow the Retraction Watch database.",
    "prereserve_doi": True}}

r = requests.post(f"{API}/deposit/depositions", json={}, headers=H, timeout=60); r.raise_for_status()
dep = r.json(); dep_id = dep["id"]; bucket = dep["links"]["bucket"]
run.log("draft_id", dep_id)
r = requests.put(f"{API}/deposit/depositions/{dep_id}", json=META, headers=H, timeout=60); r.raise_for_status()
dep = r.json()
run.log("reserved_doi", dep["metadata"]["prereserve_doi"]["doi"])
local_md5 = {}
for name in FILES:
    path = REL / name
    local_md5[name] = hashlib.md5(path.read_bytes()).hexdigest()
    with open(path, "rb") as f:
        r = requests.put(f"{bucket}/{name}", data=f, headers=H, timeout=3600); r.raise_for_status()
    run.log(f"uploaded_{name}", {"bytes": path.stat().st_size, "zenodo_checksum": r.json().get("checksum")})
r = requests.get(f"{API}/deposit/depositions/{dep_id}", headers=H, timeout=60); r.raise_for_status()
dep = r.json()
remote = {f["filename"]: f["checksum"].replace("md5:", "") for f in dep["files"]}
ok = all(remote.get(n) == local_md5[n] for n in FILES)
run.log("md5_all_match", ok); run.log("state", dep["state"]); run.log("submitted", dep["submitted"])
run.log("links", {"draft_html": dep["links"].get("html"), "latest_draft_html": dep["links"].get("latest_draft_html")})
(run.dir / "zenodo_metadata.json").write_text(json.dumps(META, indent=2))
run.finish()
if not ok: sys.exit("MD5 mismatch: check the draft")
