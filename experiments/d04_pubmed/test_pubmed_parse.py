"""Hand-built XML with known answers for pubmed_parse.py."""
import tempfile, gzip
from pathlib import Path
import pyarrow.parquet as pq
from pubmed_parse import parse_file

XML = b"""<?xml version="1.0"?><PubmedArticleSet>
<PubmedArticle><MedlineCitation><PMID Version="1">111</PMID>
<Article><Journal><ISSN IssnType="Electronic">1234-5678</ISSN><JournalIssue><PubDate><Year>2019</Year></PubDate></JournalIssue></Journal>
<ELocationID EIdType="doi">10.1/ELOC</ELocationID>
<GrantList><Grant><GrantID>R01 CA1</GrantID><Agency>NCI NIH HHS</Agency><Country>United States</Country></Grant>
<Grant><Agency>Wellcome Trust</Agency><Country>United Kingdom</Country></Grant></GrantList>
<PublicationTypeList><PublicationType UI="D016428">Journal Article</PublicationType><PublicationType UI="D016441">Retracted Publication</PublicationType></PublicationTypeList></Article>
<MedlineJournalInfo><MedlineTA>J Test</MedlineTA><NlmUniqueID>999</NlmUniqueID><ISSNLinking>1234-5678</ISSNLinking></MedlineJournalInfo>
<CommentsCorrectionsList><CommentsCorrections RefType="RetractionIn"><RefSource>J Test 2021</RefSource><PMID Version="1">222</PMID></CommentsCorrections>
<CommentsCorrections RefType="Cites"><RefSource>x</RefSource></CommentsCorrections></CommentsCorrectionsList>
<MeshHeadingList><MeshHeading><DescriptorName UI="D000001" MajorTopicYN="Y">A</DescriptorName></MeshHeading></MeshHeadingList>
</MedlineCitation><PubmedData><ArticleIdList><ArticleId IdType="pubmed">111</ArticleId><ArticleId IdType="doi">10.1/ABC</ArticleId></ArticleIdList></PubmedData></PubmedArticle>
<PubmedArticle><MedlineCitation><PMID Version="1">222</PMID><Article><Journal><JournalIssue><PubDate><MedlineDate>2021 Jan-Feb</MedlineDate></PubDate></JournalIssue></Journal>
<PublicationTypeList><PublicationType UI="D016440">Retraction of Publication</PublicationType></PublicationTypeList></Article>
<CommentsCorrectionsList><CommentsCorrections RefType="RetractionOf"><RefSource>y</RefSource><PMID Version="1">111</PMID></CommentsCorrections></CommentsCorrectionsList>
</MedlineCitation><PubmedData><ArticleIdList><ArticleId IdType="pubmed">222</ArticleId></ArticleIdList></PubmedData></PubmedArticle>
<DeleteCitation><PMID Version="1">333</PMID></DeleteCitation>
</PubmedArticleSet>"""

d = Path(tempfile.mkdtemp()); f = d / "t.xml.gz"; f.write_bytes(gzip.compress(XML))
out, stats = parse_file(f, d)
rows = pq.read_table(out).to_pylist()
a, b = rows
checks = [
    (stats == {"file": "t.xml.gz", "articles": 2, "deleted": 1}, "stats"),
    (a["pmid"] == 111 and a["doi"] == "10.1/abc", "doi from ArticleIdList wins over ELocationID"),
    (a["year"] == 2019 and b["year"] == 2021 and b["medline_date"] == "2021 Jan-Feb", "years"),
    (a["issn_electronic"] == "1234-5678" and a["issn_print"] is None and a["nlm_id"] == "999", "journal"),
    (a["pub_type_ui"] == ["D016428", "D016441"], "pub types"),
    (a["cc_reftype"] == ["RetractionIn", "Cites"] and a["cc_pmid"] == [222, None], "comments/corrections"),
    (b["cc_reftype"] == ["RetractionOf"] and b["cc_pmid"] == [111], "retraction notice"),
    (a["grant_agency"] == ["NCI NIH HHS", "Wellcome Trust"] and a["grant_id"] == ["R01 CA1", None], "grants with agency"),
    (a["mesh_ui"] == ["D000001"] and a["mesh_major"] == [True], "mesh"),
    (b["doi"] is None and b["grant_id"] == [], "missing fields"),
]
for ok, name in checks: print("PASS" if ok else "FAIL", name)
assert all(ok for ok, _ in checks)
print("ALL PASS")
