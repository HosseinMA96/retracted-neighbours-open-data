#!/usr/bin/env bash
# Download the PubMed 2026 baseline (pubmed26n0001..1334) on the VM, one file at a time, resumable, MD5-checked.
# NLM terms: free; acknowledge NLM as the source; say republished data may not be current.
set -uo pipefail
DEST=~/d/data/raw/pubmed26; mkdir -p "$DEST"; cd "$DEST"
BASE=https://ftp.ncbi.nlm.nih.gov/pubmed/baseline
curl -s -o README.txt "$BASE/README.txt"
for i in $(seq -w 1 1334); do
  f=pubmed26n$(printf %04d $((10#$i))).xml.gz
  [ -f "$f.ok" ] && continue
  for try in 1 2 3 4 5; do
    curl -s -f -C - -o "$f" "$BASE/$f" && curl -s -f -o "$f.md5" "$BASE/$f.md5" || { sleep $((try*10)); continue; }
    want=$(grep -o '[0-9a-f]\{32\}' "$f.md5"); got=$(md5sum "$f" | cut -d' ' -f1)
    if [ "$want" = "$got" ]; then touch "$f.ok"; break; else echo "md5 mismatch $f (try $try)"; rm -f "$f"; fi
  done
  [ -f "$f.ok" ] || echo "FAILED $f"
done
echo "files ok: $(ls *.ok | wc -l) / 1334; bytes: $(du -cb *.xml.gz | tail -1 | cut -f1)"
