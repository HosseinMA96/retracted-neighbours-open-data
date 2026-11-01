"""D4: streaming parser for PubMed baseline XML (lxml iterparse). One parquet per input file.
Fields: pmid, doi, pmc, year, medline_date, journal_issn (print/electronic), issn_linking, nlm_id, journal_abbrev,
publication types (UI + name), comments/corrections (RefType + PMID), MeSH descriptor UIs (+ major flag),
grants (GrantID, Agency, Country). No titles, abstracts or author names.
usage: python pubmed_parse.py OUT_DIR file1.xml.gz [file2 ...]
"""
import gzip, re, sys
from pathlib import Path
import pyarrow as pa, pyarrow.parquet as pq
from lxml import etree

SCHEMA = pa.schema([
    ("pmid", pa.int64()), ("pmid_version", pa.int16()), ("doi", pa.string()), ("pmc", pa.string()),
    ("year", pa.int16()), ("medline_date", pa.string()),
    ("issn_print", pa.string()), ("issn_electronic", pa.string()), ("issn_linking", pa.string()),
    ("nlm_id", pa.string()), ("journal_abbrev", pa.string()),
    ("pub_type_ui", pa.list_(pa.string())), ("pub_type", pa.list_(pa.string())),
    ("cc_reftype", pa.list_(pa.string())), ("cc_pmid", pa.list_(pa.int64())),
    ("mesh_ui", pa.list_(pa.string())), ("mesh_major", pa.list_(pa.bool_())),
    ("grant_id", pa.list_(pa.string())), ("grant_agency", pa.list_(pa.string())), ("grant_country", pa.list_(pa.string())),
    ("source_file", pa.string()),
])
YEAR = re.compile(r"(1[89]\d\d|20\d\d)")

def t(e):
    return None if e is None or e.text is None else e.text.strip()

def article(el, src):
    mc = el.find("MedlineCitation")
    pm = mc.find("PMID")
    art = mc.find("Article")
    j = art.find("Journal") if art is not None else None
    r = {k: None for k in SCHEMA.names}
    r["pmid"] = int(pm.text); r["pmid_version"] = int(pm.get("Version", "1")); r["source_file"] = src
    for aid in el.iterfind("PubmedData/ArticleIdList/ArticleId"):
        typ = aid.get("IdType")
        if typ == "doi" and r["doi"] is None and aid.text: r["doi"] = aid.text.strip().lower()
        elif typ == "pmc" and r["pmc"] is None and aid.text: r["pmc"] = aid.text.strip()
    if r["doi"] is None and art is not None:      # fallback: ELocationID
        for e in art.iterfind("ELocationID"):
            if e.get("EIdType") == "doi" and e.text: r["doi"] = e.text.strip().lower(); break
    if j is not None:
        for issn in j.iterfind("ISSN"):
            key = "issn_electronic" if issn.get("IssnType") == "Electronic" else "issn_print"
            r[key] = t(issn)
        pd = j.find("JournalIssue/PubDate")
        if pd is not None:
            y = t(pd.find("Year"))
            md = t(pd.find("MedlineDate"))
            r["medline_date"] = md
            m = YEAR.search(y or md or "")
            r["year"] = int(m.group(1)) if m else None
    info = mc.find("MedlineJournalInfo")
    if info is not None:
        r["issn_linking"] = t(info.find("ISSNLinking")); r["nlm_id"] = t(info.find("NlmUniqueID"))
        r["journal_abbrev"] = t(info.find("MedlineTA"))
    pts = art.findall("PublicationTypeList/PublicationType") if art is not None else []
    r["pub_type_ui"] = [p.get("UI") for p in pts]; r["pub_type"] = [t(p) for p in pts]
    ccs = mc.findall("CommentsCorrectionsList/CommentsCorrections")
    r["cc_reftype"] = [c.get("RefType") for c in ccs]
    r["cc_pmid"] = [int(t(c.find("PMID"))) if t(c.find("PMID")) and t(c.find("PMID")).isdigit() else None for c in ccs]
    ms = mc.findall("MeshHeadingList/MeshHeading/DescriptorName")
    r["mesh_ui"] = [m.get("UI") for m in ms]; r["mesh_major"] = [m.get("MajorTopicYN") == "Y" for m in ms]
    gs = art.findall("GrantList/Grant") if art is not None else []
    r["grant_id"] = [t(g.find("GrantID")) for g in gs]
    r["grant_agency"] = [t(g.find("Agency")) for g in gs]
    r["grant_country"] = [t(g.find("Country")) for g in gs]
    return r

def parse_file(path, out_dir):
    path = Path(path); out = Path(out_dir) / (path.name.replace(".xml.gz", "").replace(".xml", "") + ".parquet")
    if out.exists(): return out, None
    rows, deleted = [], []
    op = gzip.open if path.suffix == ".gz" else open
    with op(path, "rb") as f:
        for _, el in etree.iterparse(f, events=("end",), tag=("PubmedArticle", "DeleteCitation"), huge_tree=True):
            if el.tag == "PubmedArticle":
                rows.append(article(el, path.name))
            else:
                deleted += [int(p.text) for p in el.iterfind("PMID")]
            el.clear()
            while el.getprevious() is not None: del el.getparent()[0]
    tmp = out.with_suffix(".tmp")
    pq.write_table(pa.Table.from_pylist(rows, schema=SCHEMA), tmp, compression="zstd"); tmp.rename(out)
    return out, {"file": path.name, "articles": len(rows), "deleted": len(deleted)}

if __name__ == "__main__":
    out_dir = Path(sys.argv[1]); out_dir.mkdir(parents=True, exist_ok=True)
    for p in sys.argv[2:]:
        print(parse_file(p, out_dir))
