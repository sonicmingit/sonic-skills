#!/usr/bin/env bash
set -euo pipefail

# Manual updater for Feishu/Lark OpenClaw plugin (@larksuite/openclaw-lark)
#
# Default behavior is conservative:
# - move existing extension dir to a timestamped backup (no rm)
# - download via `npm pack`
# - extract to a temp dir, then install into ~/.openclaw/extensions/larksuite-openclaw-plugin
# - verify ~/.openclaw/openclaw.json contains plugins.allow including "openclaw-lark"

VERSION=""
FIX_ALLOW=0
KEEP_TGZ=0

BEFORE_VERSION=""
AFTER_VERSION=""

usage() {
  cat <<'USAGE'
Usage:
  update-openclaw-lark.sh [--version <ver>] [--fix-plugins-allow] [--keep-tgz]

Options:
  --version <ver>         Install a specific version, e.g. 2026.3.17
  --fix-plugins-allow     If openclaw.json plugins.allow is missing openclaw-lark, add it
  --keep-tgz              Keep downloaded tgz in ~/.openclaw/extensions for debugging
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      VERSION="${2:-}"; shift 2 ;;
    --fix-plugins-allow)
      FIX_ALLOW=1; shift ;;
    --keep-tgz)
      KEEP_TGZ=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2
      ;;
  esac
done

EXT_DIR="$HOME/.openclaw/extensions"
TARGET_DIR="$EXT_DIR/larksuite-openclaw-plugin"
BACKUP_ROOT="$EXT_DIR/_backup"
OPENCLAW_JSON="$HOME/.openclaw/openclaw.json"

LAST_BACKUP=""

on_err() {
  echo "" >&2
  echo "ERROR: update failed." >&2
  if [[ -n "${LAST_BACKUP:-}" && -d "$LAST_BACKUP" ]]; then
    echo "Rollback (restore previous plugin):" >&2
    echo "  mv '$LAST_BACKUP' '$TARGET_DIR'" >&2
  else
    echo "No backup folder recorded (nothing to rollback)." >&2
  fi
}
trap on_err ERR

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }
}

need_cmd npm
need_cmd tar
need_cmd node

get_pkg_version() {
  local dir="$1"
  local f="$dir/package.json"
  if [[ ! -f "$f" ]]; then
    echo ""; return 0
  fi
  node -e "const fs=require('fs'); const p=process.argv[1]; try{const j=JSON.parse(fs.readFileSync(p,'utf8')); process.stdout.write(String(j.version||''));}catch(e){process.stdout.write('');}" "$f"
}

mkdir -p "$EXT_DIR" "$BACKUP_ROOT"

cd "$EXT_DIR"

echo "[1/6] Environment"
echo "- extensions dir: $EXT_DIR"

# capture current installed version (if any)
if [[ -d "$TARGET_DIR" ]]; then
  BEFORE_VERSION="$(get_pkg_version "$TARGET_DIR")"
fi
if [[ -n "$BEFORE_VERSION" ]]; then
  echo "- current openclaw-lark plugin version: $BEFORE_VERSION"
else
  echo "- current openclaw-lark plugin version: (unknown / not installed)"
fi

echo "[2/6] Backup existing plugin (if any)"
if [[ -d "$TARGET_DIR" ]]; then
  TS="$(date +%Y%m%d-%H%M%S)"
  BK="$BACKUP_ROOT/larksuite-openclaw-plugin.$TS"
  echo "- moving $TARGET_DIR -> $BK"
  mv "$TARGET_DIR" "$BK"
  LAST_BACKUP="$BK"
else
  echo "- no existing $TARGET_DIR (skip backup move)"
fi

echo "[3/6] Download via npm pack"
SPEC="@larksuite/openclaw-lark"
if [[ -n "$VERSION" ]]; then
  SPEC="@larksuite/openclaw-lark@$VERSION"
fi

echo "- npm pack $SPEC"
TGZ="$(npm pack "$SPEC" | tail -n 1)"

if [[ ! -f "$TGZ" ]]; then
  echo "npm pack did not produce tgz as expected." >&2
  exit 1
fi

echo "- downloaded: $EXT_DIR/$TGZ"

echo "[4/6] Extract to temp dir"
TMPDIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMPDIR" || true
}
trap cleanup EXIT

tar -xzf "$TGZ" -C "$TMPDIR"

if [[ ! -d "$TMPDIR/package" ]]; then
  echo "Unexpected tgz layout: missing $TMPDIR/package" >&2
  echo "Contents:" >&2
  ls -la "$TMPDIR" >&2 || true
  exit 1
fi

echo "[5/6] Install extracted package as extension"
# The plugin root should be the extracted package directory.
# Preserve the canonical folder name expected by OpenClaw: larksuite-openclaw-plugin
mv "$TMPDIR/package" "$TARGET_DIR"

# capture new installed version
AFTER_VERSION="$(get_pkg_version "$TARGET_DIR")"

if [[ -n "$AFTER_VERSION" ]]; then
  echo "- installed to: $TARGET_DIR (version: $AFTER_VERSION)"
else
  echo "- installed to: $TARGET_DIR (version: unknown)"
fi

if [[ -n "$BEFORE_VERSION" && -n "$AFTER_VERSION" ]]; then
  echo "- version change: $BEFORE_VERSION -> $AFTER_VERSION"
elif [[ -z "$BEFORE_VERSION" && -n "$AFTER_VERSION" ]]; then
  echo "- version change: (fresh install) -> $AFTER_VERSION"
fi

echo "\nPost-install verification:"
if command -v openclaw >/dev/null 2>&1; then
  echo "- openclaw plugins list (best effort)"
  openclaw plugins list || true
  echo "- openclaw status (best effort)"
  openclaw status || true
else
  echo "WARN: openclaw command not found in PATH; skip verification" >&2
fi

if [[ "$KEEP_TGZ" -eq 0 ]]; then
  rm -f "$TGZ" || true
fi

echo "[6/6] Verify/patch openclaw.json plugins.allow"
if [[ ! -f "$OPENCLAW_JSON" ]]; then
  echo "WARN: $OPENCLAW_JSON not found; cannot verify plugins.allow" >&2
  exit 0
fi

# Use node to parse and optionally patch JSON (jq may not exist)
OPENCLAW_JSON="$OPENCLAW_JSON" FIX_ALLOW="$FIX_ALLOW" node <<'NODE'
const fs = require('fs');

const openclawJson = process.env.OPENCLAW_JSON;
const fix = process.env.FIX_ALLOW === '1';

const raw = fs.readFileSync(openclawJson, 'utf8');
let obj;
try { obj = JSON.parse(raw); } catch (e) {
  console.error('ERROR: openclaw.json is not valid JSON:', e.message);
  process.exit(1);
}

obj.plugins ??= {};

// allow could be missing entirely; tolerate that.
const allow = obj.plugins.allow;
const has = Array.isArray(allow) && allow.includes('openclaw-lark');

if (has) {
  console.log('OK: plugins.allow already contains openclaw-lark');
  process.exit(0);
}

if (!fix) {
  console.log('WARN: plugins.allow does not contain openclaw-lark (or plugins.allow missing).');
  console.log('Run with --fix-plugins-allow to auto-add it, or edit manually:');
  console.log('  ~/.openclaw/openclaw.json -> plugins.allow: ["openclaw-lark", ...]');
  process.exit(0);
}

// If allow is missing, initialize as []
obj.plugins.allow = Array.isArray(allow) ? allow.slice() : [];
if (!obj.plugins.allow.includes('openclaw-lark')) obj.plugins.allow.unshift('openclaw-lark');

// Write pretty JSON while keeping it stable
fs.writeFileSync(openclawJson, JSON.stringify(obj, null, 2) + '\n');
console.log('FIXED: added openclaw-lark to plugins.allow');
NODE
