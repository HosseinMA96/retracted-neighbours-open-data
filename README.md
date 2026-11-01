# Retracted neighbours and future retractions: code, pre-registration and run records

Companion repository to the paper

> Hossein Mohasel Arjomandi. *Do links to retracted papers predict future retractions? An out-of-sample test on the
> open biomedical citation graph.* Manuscript submitted for publication.

The study computes, on the OpenCitations snapshot of January 2024, how many references of each biomedical paper point
to papers retracted by 31 January 2024 (and how many citations it received from them), freezes these scores, and
compares them with retractions recorded in the Retraction Watch database from February 2024 to October 2026. The
design was pre-registered. Supporting analyses cover community concentration, NIH-funded papers that cite retracted
work, and citations around retraction.

## Contents
| Path | What it holds |
|---|---|
| `FINDINGS.md` | Map from every number in the paper to the run that produced it |
| `REPRODUCE.md` | Inputs and checksums, environment, the exact commands in order, determinism notes, and runs not cited |
| `experiments/d07_prereg/PREREGISTRATION.md` | The pre-registration; its SHA-256 was recorded before any score was computed, and the evaluation script verifies the frozen score files before reading outcomes |
| `experiments/dNN_*/` | Scripts, lab notebook (`RESULTS_LOG.md`) and one folder per run (`run.json`, `stdout.log`, small outputs, `SHA256SUMS`) |
| `paper/` | LaTeX source, figures (made by `experiments/d13_figures/`), references with DOI verification (`bib_verification.tsv`) |
| `lit/LIT.md` | Literature search records and the gap statement |
| `vm/` | Scripts for the steps that need a large machine (64 GB RAM) and the environment lock file |

## Data
Inputs are public but not included because of their size: the parsed OpenCitations snapshot (Illinois Data Bank,
doi:10.13012/B2IDB-5216575_V1), OpenCitations Meta (doi:10.6084/m9.figshare.21747461.v7), the Retraction Watch
database (Crossref, GitLab commit `a98cc7e`), and the PubMed 2026 baseline (NLM). The derived dataset (retracted
papers with their citation neighbourhoods and retraction dates) is deposited separately: TODO(Zenodo DOI).

## What is not here, by design
No author names and no score, rank or list of non-retracted papers: a high score is a reason to look, not evidence of a
problem, and many papers cite retracted work for legitimate reasons. A retraction is a public editorial label and does
not by itself imply misconduct.

## Licences
Code: MIT (`LICENSE`). Run records, tables, figures and documentation: CC BY 4.0 (`LICENSE-DATA`). Inputs keep their
own terms.

## Generative AI
Claude Opus 5.5 (Anthropic) was used as a coding and writing assistant under the author's direction; the author checked
all analyses, numbers and references.
