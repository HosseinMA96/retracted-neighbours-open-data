"""D2: frozen Retraction Watch copy -> paper-level table and descriptive counts.
No author, institution or title fields are kept. Counting only: no citation data and no scores are touched here.
usage: python d02_rw_counts.py RUN_ID [path/to/retraction_watch.csv]
"""
import re, subprocess, sys
from pathlib import Path
import pandas as pd
from common import Run, D_DATA, sha256

T0 = pd.Timestamp("2024-01-31")          # provisional snapshot cutoff; TODO(verify) against the Data Bank README
CSV = Path(sys.argv[2]) if len(sys.argv) > 2 else D_DATA / "raw/retraction-watch-data/retraction_watch.csv"
git = subprocess.run(["git", "-C", str(CSV.parent), "log", "-1", "--format=%H %cI"], capture_output=True, text=True).stdout.strip()
run = Run(sys.argv[1], __file__, {"csv": str(CSV), "csv_sha256": sha256(CSV), "repo_commit": git, "T0": str(T0.date())})

d = pd.read_csv(CSV, dtype=str, encoding="utf-8", keep_default_na=False)
d = d.drop(columns=[c for c in d.columns if c.startswith("Unnamed")])
run.log("rows", len(d)); run.log("columns", list(d.columns))

def clean_doi(s):
    s = s.strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    return s if s.startswith("10.") else None
def clean_pmid(s):
    s = s.strip()
    return int(s) if s.isdigit() and int(s) > 0 else None
def date(s):
    return pd.to_datetime(s, format="%m/%d/%Y %H:%M", errors="coerce")

x = pd.DataFrame({
    "record_id": d["Record ID"].astype(int),
    "nature": d["RetractionNature"].str.strip(),
    "doi": d["OriginalPaperDOI"].map(clean_doi),
    "pmid": d["OriginalPaperPubMedID"].map(clean_pmid),
    "notice_doi": d["RetractionDOI"].map(clean_doi),
    "notice_pmid": d["RetractionPubMedID"].map(clean_pmid),
    "notice_date": date(d["RetractionDate"]),
    "paper_date": date(d["OriginalPaperDate"]),
    "article_type": d["ArticleType"].str.strip(";").str.strip(),
    "subject": d["Subject"],
    "reasons": d["Reason"].map(lambda s: [r.strip().lstrip("+").strip() for r in s.split(";") if r.strip()]),
    "journal": d["Journal"], "publisher": d["Publisher"],
})
run.log("unparsed_notice_date", int(x.notice_date.isna().sum()))
run.log("unparsed_paper_date", int(x.paper_date.isna().sum()))
run.log("rows_by_nature", x.nature.value_counts().to_dict())
x["biomed_subject"] = x.subject.str.contains(r"\((?:BLS|HSC)\)", regex=True)
x["paper_mill"] = x.reasons.map(lambda r: any("paper mill" in s.lower() for s in r))

r = x[x.nature == "Retraction"].copy()
run.log("retraction_rows", len(r))
run.log("retraction_rows_with_doi", int(r.doi.notna().sum()))
run.log("retraction_rows_with_pmid", int(r.pmid.notna().sum()))
run.log("retraction_rows_with_doi_or_pmid", int((r.doi.notna() | r.pmid.notna()).sum()))
run.log("retraction_rows_with_neither", int((r.doi.isna() & r.pmid.isna()).sum()))
run.log("retraction_rows_biomed_subject", int(r.biomed_subject.sum()))
run.log("retraction_rows_pmid_or_biomed_subject", int((r.pmid.notna() | r.biomed_subject).sum()))
run.log("retraction_rows_duplicate_doi", int(r.doi.dropna().duplicated().sum()))
run.log("retraction_rows_duplicate_pmid", int(r.pmid.dropna().duplicated().sum()))

# Paper level: key = DOI if present, else PMID. Earliest retraction notice wins; reasons are unioned.
r["key"] = r.doi.where(r.doi.notna(), "pmid:" + r.pmid.astype("Int64").astype(str))
r = r[r.key.notna() & (r.key != "pmid:<NA>")]
p = (r.sort_values("notice_date").groupby("key", as_index=False)
       .agg(doi=("doi", "first"), pmid=("pmid", "first"), notice_date=("notice_date", "min"),
            paper_date=("paper_date", "first"), n_notices=("record_id", "size"), record_ids=("record_id", list),
            reasons=("reasons", lambda s: sorted({v for l in s for v in l})), paper_mill=("paper_mill", "max"),
            biomed_subject=("biomed_subject", "max"), article_type=("article_type", "first"),
            journal=("journal", "first"), publisher=("publisher", "first")))
reinst = x[x.nature == "Reinstatement"]
reinst_keys = set(reinst.doi.dropna()) | {f"pmid:{int(v)}" for v in reinst.pmid.dropna()}
p["reinstated"] = p.key.isin(reinst_keys)
p["retracted_by_T0"] = p.notice_date <= T0
p["retracted_after_T0"] = p.notice_date > T0
p["paper_year"] = p.paper_date.dt.year
p["notice_year"] = p.notice_date.dt.year
p["lag_years"] = (p.notice_date - p.paper_date).dt.days / 365.25
run.log("papers", len(p))
run.log("papers_with_pmid", int(p.pmid.notna().sum()))
run.log("papers_reinstated", int(p.reinstated.sum()))
run.log("papers_no_notice_date", int(p.notice_date.isna().sum()))
run.log("papers_retracted_by_T0", int(p.retracted_by_T0.sum()))
run.log("papers_retracted_after_T0", int(p.retracted_after_T0.sum()))
bio = p.pmid.notna() | p.biomed_subject
run.log("biomed_papers_retracted_by_T0", int((bio & p.retracted_by_T0).sum()))
run.log("biomed_papers_retracted_after_T0", int((bio & p.retracted_after_T0).sum()))
post = p[p.retracted_after_T0 & bio]
run.log("biomed_after_T0_paper_year_2015_2023", int(post.paper_year.between(2015, 2023).sum()))
run.log("biomed_after_T0_paper_year_2010_2023", int(post.paper_year.between(2010, 2023).sum()))
run.log("biomed_after_T0_paper_year_2015_2023_paper_mill", int((post.paper_year.between(2015, 2023) & post.paper_mill).sum()))
run.log("biomed_after_T0_by_notice_year", post.notice_year.value_counts().sort_index().to_dict())
run.log("biomed_after_T0_by_paper_year", post.paper_year.value_counts().sort_index().loc[2000:].to_dict())
run.log("biomed_after_T0_with_pmid", int(post.pmid.notna().sum()))
run.log("paper_mill_papers", int(p.paper_mill.sum()))
run.log("paper_mill_by_notice_year", p[p.paper_mill].notice_year.value_counts().sort_index().to_dict())
run.log("retractions_by_notice_year", p.notice_year.value_counts().sort_index().to_dict())
run.log("median_lag_years_biomed_by_T0", round(float(p[bio & p.retracted_by_T0].lag_years.median()), 2))
run.log("median_lag_years_biomed_after_T0", round(float(post.lag_years.median()), 2))

reasons = pd.Series([v for l in p.reasons for v in l]).value_counts()
reasons.rename_axis("reason").rename("papers").to_csv(run.dir / "reason_counts.csv")
p.groupby(["notice_year", "paper_mill"]).size().rename("papers").to_csv(run.dir / "papers_by_notice_year_mill.csv")
(D_DATA / "work").mkdir(parents=True, exist_ok=True)
out = D_DATA / "work" / f"rw_papers_{sys.argv[1]}.parquet"
p.to_parquet(out, index=False)
run.log("paper_table", {"path": str(out), "rows": len(p), "sha256": sha256(out)})
run.finish()
