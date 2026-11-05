#!/usr/bin/env bash
set -euo pipefail

PRINTER="${PRINTER:-Brother_T725DW}"
TITLE="${TITLE:-OpenClaw print}"
COPIES="${COPIES:-1}"

usage() {
  cat <<'EOF'
Usage:
  PRINTER=Brother_T725DW COPIES=1 TITLE='My job' ./print_file.sh <file>

Notes:
- Requires CUPS (lp/lpstat) installed.
- This script does NOT handle credentials.
EOF
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" || $# -lt 1 ]]; then
  usage
  exit 0
fi

FILE="$1"
if [[ ! -f "$FILE" ]]; then
  echo "File not found: $FILE" >&2
  exit 2
fi

echo "[print] printer=$PRINTER copies=$COPIES title=$TITLE file=$FILE"

FILE_TO_PRINT="$FILE"
PREP_STEP=""
# Auto-handle exam PDFs: strip tail answer pages if detected.
# Enable with EXAM_MODE=auto (default). Disable with EXAM_MODE=off.
EXAM_MODE="${EXAM_MODE:-auto}"
if [[ "$EXAM_MODE" != "off" && "${FILE,,}" == *.pdf ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  PREP="$SCRIPT_DIR/prepare_pdf_for_print.sh"
  if [[ -x "$PREP" ]]; then
    OUT_PREP="$(mktemp --suffix=.pdf)"
    PREP_OUT="$("$PREP" "$FILE" "$OUT_PREP" 2>&1)" || true
    if [[ -f "$OUT_PREP" ]] && grep -q "answer=no" <<<"$PREP_OUT"; then
      FILE_TO_PRINT="$OUT_PREP"
      PREP_STEP="✅ 未检测到答案页，打印全文"
    elif [[ -f "$OUT_PREP" ]] && grep -q "answer=yes" <<<"$PREP_OUT"; then
      FILE_TO_PRINT="$OUT_PREP"
      STRIP_INFO=$(grep "strip_from_page=" <<<"$PREP_OUT" | head -1)
      PREP_STEP="✂️ 检测到答案页，已去除（从第 $(echo "$STRIP_INFO" | cut -d= -f2) 页起）"
    else
      echo "[print] prepare_pdf_for_print failed; printing original PDF" >&2
      echo "$PREP_OUT" >&2
      rm -f "$OUT_PREP" || true
    fi
  fi
fi

# -n copies; -t title
lp -d "$PRINTER" -n "$COPIES" -t "$TITLE" "$FILE_TO_PRINT"

if [[ -n "$PREP_STEP" ]]; then
  echo "$PREP_STEP"
fi

echo
echo "[queue] lpstat -o"
lpstat -o || true
