#!/usr/bin/env bash
set -euo pipefail

# OCR selected PDF pages into a single text file (stdout).
# Dependencies: pdftoppm (poppler-utils), tesseract

PDF="$1"
PAGES_SPEC="$2"  # e.g. "1-2,38-40" or "1" or "5-7"
LANG="${OCR_LANG:-chi_sim+eng}"
DPI="${OCR_DPI:-200}"

if [[ -z "$PDF" || ! -f "$PDF" ]]; then
  echo "PDF not found: $PDF" >&2
  exit 2
fi

if [[ -z "$PAGES_SPEC" ]]; then
  echo "Missing pages spec" >&2
  exit 2
fi

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Expand pages spec to a list of page numbers
python3 - "$PAGES_SPEC" >"$TMPDIR/pages.txt" <<'PY'
import re, sys
spec=sys.argv[1].strip()
parts=[p.strip() for p in spec.split(',') if p.strip()]
nums=[]
for part in parts:
  m=re.fullmatch(r'(\d+)-(\d+)', part)
  if m:
    a,b=map(int,m.groups())
    if a<=b:
      nums.extend(range(a,b+1))
    else:
      nums.extend(range(b,a+1))
  else:
    nums.append(int(part))
# de-dupe preserve order
seen=set(); out=[]
for n in nums:
  if n not in seen:
    seen.add(n); out.append(n)
print('\n'.join(str(n) for n in out))
PY

while read -r p; do
  [[ -z "$p" ]] && continue
  IMG_PREFIX="$TMPDIR/p${p}"
  # Render one page to PNG
  pdftoppm -f "$p" -l "$p" -r "$DPI" -png "$PDF" "$IMG_PREFIX" >/dev/null 2>&1 || true
  IMG="$IMG_PREFIX-$(printf "%d" "$p").png"
  # poppler naming may also be $IMG_PREFIX-1.png for single page; fallback
  if [[ ! -f "$IMG" ]]; then
    IMG="$IMG_PREFIX-1.png"
  fi
  if [[ ! -f "$IMG" ]]; then
    continue
  fi
  # OCR to txt (stdout)
  tesseract "$IMG" stdout -l "$LANG" 2>/dev/null || true
  echo "\n"
done <"$TMPDIR/pages.txt"
