#!/usr/bin/env bash
set -euo pipefail

# Prepare a PDF for printing.
# If the PDF looks like an exam paper, and the tail pages look like answers,
# output a new PDF with the tail answer pages stripped.
#
# Dependencies: pdfinfo, pdftotext, gs

INFILE="$1"
OUTFILE="${2:-}"

if [[ -z "$INFILE" || ! -f "$INFILE" ]]; then
  echo "Input PDF not found: $INFILE" >&2
  exit 2
fi

if [[ -z "$OUTFILE" ]]; then
  OUTFILE="${INFILE%.pdf}.prepared.pdf"
fi

# Keywords (override via env)
EXAM_KEYWORDS_REGEX="${EXAM_KEYWORDS_REGEX:-试卷|卷子|考试|语文|数学|英语|模拟|复习}"
# Include common headings like "最终答案汇总" (answers summary)
ANSWER_KEYWORDS_REGEX="${ANSWER_KEYWORDS_REGEX:-最终答案汇总|答案汇总|参考答案|参考\s*答案|答案解析|答案|解析|解答|Answer[[:space:]]*Key|Answers?}"
# How many tail pages to inspect for answer keywords (min tail window)
TAIL_SCAN_PAGES="${TAIL_SCAN_PAGES:-3}"
# Alternatively scan a fraction of the document tail (e.g. 0.25 means last 1/4)
TAIL_SCAN_FRACTION="${TAIL_SCAN_FRACTION:-0}"
# Hard cap for tail scan pages (avoid too slow OCR on huge PDFs)
TAIL_SCAN_MAX_PAGES="${TAIL_SCAN_MAX_PAGES:-20}"
# If set to 1, do not strip anything
PRINT_ALL="${PRINT_ALL:-0}"

if [[ "$PRINT_ALL" == "1" ]]; then
  cp -f "$INFILE" "$OUTFILE"
  echo "$OUTFILE"
  exit 0
fi

# Total pages
PAGES=$(pdfinfo "$INFILE" | awk -F: '/^Pages/ {gsub(/ /, "", $2); print $2}')
if [[ -z "$PAGES" ]]; then
  echo "Failed to parse page count via pdfinfo" >&2
  exit 3
fi

# Detect if this looks like an exam paper.
# Strategy: try pdftotext first; if no hits (or empty), fallback to OCR on first pages.
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

FIRST_TXT="$TMPDIR/first.txt"
# pdftotext returns non-zero for some PDFs; ignore and proceed with what we got
pdftotext -f 1 -l 2 "$INFILE" "$FIRST_TXT" 2>/dev/null || true

is_exam=0
if [[ -s "$FIRST_TXT" ]] && grep -Eqi "$EXAM_KEYWORDS_REGEX" "$FIRST_TXT"; then
  is_exam=1
else
  # OCR fallback (only if tool exists)
  OCR_TOOL="$(cd "$(dirname "$0")" && pwd)/ocr_pdf_pages.sh"
  if [[ -x "$OCR_TOOL" ]]; then
    OCR_FIRST="$TMPDIR/first_ocr.txt"
    "$OCR_TOOL" "$INFILE" "1-2" >"$OCR_FIRST" || true
    if [[ -s "$OCR_FIRST" ]] && grep -Eqi "$EXAM_KEYWORDS_REGEX" "$OCR_FIRST"; then
      is_exam=1
    fi
  fi

  # Metadata fallback (Title/Subject) — helps for scanned PDFs where pdftotext/OCR miss keywords
  if [[ "$is_exam" != "1" ]]; then
    META_TXT="$TMPDIR/meta.txt"
    pdfinfo "$INFILE" 2>/dev/null | awk -F: 'tolower($1) ~ /^(title|subject)$/ {print $2}' >"$META_TXT" || true
    if [[ -s "$META_TXT" ]] && grep -Eqi "$EXAM_KEYWORDS_REGEX" "$META_TXT"; then
      is_exam=1
    fi
  fi
fi

# If not detected as exam, we can still scan the document tail for answer keywords
# when TAIL_SCAN_FRACTION>0 (safer than scanning entire document).
if [[ "$is_exam" != "1" ]]; then
  if [[ "$TAIL_SCAN_FRACTION" == "0" || "$TAIL_SCAN_FRACTION" == "0.0" ]]; then
    # Not an exam and no tail-fraction scanning requested: passthrough
    cp -f "$INFILE" "$OUTFILE"
    echo "$OUTFILE"
    exit 0
  fi
fi

# Scan tail pages for answer keywords; find earliest tail page that matches.
# Strategy: pdftotext first; if no hits, OCR fallback on tail pages.
# Determine tail scan window:
# - always at least TAIL_SCAN_PAGES
# - if TAIL_SCAN_FRACTION>0, also scan last ceil(PAGES*fraction)
# - cap at TAIL_SCAN_MAX_PAGES

scan_pages=$TAIL_SCAN_PAGES
if [[ "$TAIL_SCAN_FRACTION" != "0" && "$TAIL_SCAN_FRACTION" != "0.0" ]]; then
  frac_pages=$(python3 - "$PAGES" "$TAIL_SCAN_FRACTION" <<'PY'
import math, sys
pages=int(sys.argv[1]); frac=float(sys.argv[2])
print(int(math.ceil(pages*frac)))
PY
)
  if [[ "$frac_pages" -gt "$scan_pages" ]]; then scan_pages=$frac_pages; fi
fi
if [[ "$scan_pages" -gt "$TAIL_SCAN_MAX_PAGES" ]]; then scan_pages=$TAIL_SCAN_MAX_PAGES; fi

START=$((PAGES-scan_pages+1))
if (( START < 1 )); then START=1; fi

ANSWER_START=0
for ((p=START; p<=PAGES; p++)); do
  T="$TMPDIR/p${p}.txt"
  pdftotext -f "$p" -l "$p" "$INFILE" "$T" 2>/dev/null || true
  if [[ -s "$T" ]] && grep -Eqi "$ANSWER_KEYWORDS_REGEX" "$T"; then
    ANSWER_START=$p
    break
  fi

  # OCR fallback for this page
  OCR_TOOL="$(cd "$(dirname "$0")" && pwd)/ocr_pdf_pages.sh"
  if [[ -x "$OCR_TOOL" ]]; then
    OCR_T="$TMPDIR/p${p}.ocr.txt"
    "$OCR_TOOL" "$INFILE" "$p" >"$OCR_T" || true
    if [[ -s "$OCR_T" ]] && grep -Eqi "$ANSWER_KEYWORDS_REGEX" "$OCR_T"; then
      ANSWER_START=$p
      break
    fi
  fi
done

if (( ANSWER_START == 0 )); then
  # No answer keywords found in tail: passthrough
  cp -f "$INFILE" "$OUTFILE"
  echo "answer=no"
  echo "$OUTFILE"
  exit 0
fi

# Strip from ANSWER_START..PAGES (tail only)
KEEP_LAST=$((ANSWER_START-1))
if (( KEEP_LAST < 1 )); then
  echo "Detected answers start at page 1; refusing to strip entire doc. Set PRINT_ALL=1 to override." >&2
  exit 4
fi

echo "answer=yes strip_from_page=$ANSWER_START"

# Generate contiguous-range PDF using Ghostscript
# -dSAFER: reduce risk when processing PDFs
# -dFirstPage/-dLastPage: keep 1..KEEP_LAST

gs -q -dNOPAUSE -dBATCH -dSAFER -sDEVICE=pdfwrite \
  -dFirstPage=1 -dLastPage="$KEEP_LAST" \
  -sOutputFile="$OUTFILE" \
  "$INFILE"

echo "$OUTFILE"
