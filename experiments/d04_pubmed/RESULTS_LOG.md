# D4 PubMed 2026 baseline: lab notebook

## Download (2026-11-01, VM)
- `vm/download_pubmed.sh`: https://ftp.ncbi.nlm.nih.gov/pubmed/baseline, files pubmed26n0001–1334, one at a time, every file MD5-checked against NLM's `.md5`. **1334/1334 OK, 54,267,874,919 bytes.** README "Last Updated January 30, 2026"; the 2026 baseline was released Dec 2025, so its retraction flags reflect about Dec 2025.
- NLM terms (baseline README): free; acknowledge NLM as the source "in a clear and conspicuous manner"; no PubMed logo or implied endorsement; anyone who republishes must keep it current or say it may not be current; some abstracts are copyrighted (D keeps no abstracts).

## Parser
- `pubmed_parse.py`: lxml `iterparse`, one parquet per file. Keeps PMID, DOI (ArticleIdList, fallback ELocationID), PMC, year (Year or MedlineDate), ISSNs, NLM ID, publication types (UI + name), CommentsCorrections (RefType + PMID), MeSH descriptor UIs with major flag, grants **with Agency and Country**. No titles, abstracts or author names.
- Why a new parser: `pubmed-meta-etl/parallel.py:188–196` keeps only `GrantID`, so NIH grants cannot be told apart.
- `test_pubmed_parse.py`: hand-built XML with known answers, 10 checks, **ALL PASS** (laptop and VM). One real file: pubmed26n0001, 30,000 articles in 5.7 s.

## d04_pubmed_20261101_01 (1,958 s; 7 processes)
- 39,994,988 articles in all files, **39,994,988 distinct PMIDs** (no duplicates across baseline files); 0 DeleteCitation elements.
- With DOI 31,080,408 (11,151 DOI values shared by more than one PMID); with year 39,994,076.
- Publication type Retracted Publication (D016441): **30,697**; Retraction of Publication (D016440): 29,990.
- CommentsCorrections: RetractionIn 30,861 (on 30,695 articles), RetractionOf 30,305, ExpressionOfConcernIn 3,798, ErratumIn 337,002.
- Grants: 5,387,901 articles with any grant; **3,341,220 with an agency containing "NIH"**. Top agencies: NCI NIH HHS 1,352,584; NHLBI NIH HHS 1,084,323; NIGMS NIH HHS 879,167; NIAID NIH HHS 774,814; … (full list in run.json).
- Output `~/d/data/work/pubmed26.parquet` (1.85 GB).
- Note for RQ3: PubMed `GrantList` is known to be incomplete for older papers; cross-check with NIH RePORTER link tables is still TODO (D3).
