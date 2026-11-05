#!/usr/bin/env python3
"""Generate an image via an OpenAI-compatible API serving Gemini image models.

- Reads defaults from ~/openclaw/secrets.yaml: models.1821gemini.base_url + api_key
- Calls chat.completions.create(model=..., extra_body={"size": ...})
- Tries to extract an image from response.choices[0].message.content:
  - data URL (data:image/png;base64,....)
  - raw base64 (best-effort)
  - http(s) URL (downloads)

Never prints the API key.
"""

import argparse
import base64
import os
import re
import sys
import urllib.request
from pathlib import Path


def load_secrets():
    p = Path.home() / "openclaw" / "secrets.yaml"
    if not p.exists():
        return {}
    try:
        import yaml  # type: ignore
    except Exception:
        return {}

    try:
        with p.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def get_nested(d, path):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def try_extract_data_url(s: str):
    m = re.search(r"data:image/(?P<fmt>png|jpeg|jpg|webp);base64,(?P<b64>[A-Za-z0-9+/=\n\r]+)", s)
    if not m:
        return None
    fmt = m.group("fmt").replace("jpg", "jpeg")
    b64 = m.group("b64")
    b = base64.b64decode(b64)
    return fmt, b


def try_extract_url(s: str):
    m = re.search(r"https?://\S+", s)
    if not m:
        return None
    # strip common trailing punctuation
    return m.group(0).rstrip(')];,\"\'')


def try_extract_raw_base64(s: str):
    # Heuristic: a long base64-ish blob
    cand = re.sub(r"\s+", "", s)
    if len(cand) < 2000:
        return None
    if not re.fullmatch(r"[A-Za-z0-9+/=]+", cand):
        return None
    try:
        b = base64.b64decode(cand)
    except Exception:
        return None
    return b


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-sonic/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True, help="Output image path, e.g. /tmp/openclaw/out.png")
    ap.add_argument("--size", default="1024x1024", help="e.g. 1024x1024, 1280x720, 720x1280")
    ap.add_argument("--model", default="gemini-3-pro-image")
    ap.add_argument("--base-url", dest="base_url", default="")
    ap.add_argument("--api-key", dest="api_key", default="")
    args = ap.parse_args()

    secrets = load_secrets()
    base_url = args.base_url or get_nested(secrets, ["models", "1821gemini", "base_url"]) or ""
    api_key = args.api_key or get_nested(secrets, ["models", "1821gemini", "api_key"]) or ""

    if not base_url:
        print("ERROR: base_url not provided and not found at secrets.yaml models.1821gemini.base_url", file=sys.stderr)
        sys.exit(2)
    if not api_key:
        print("ERROR: api_key not provided and not found at secrets.yaml models.1821gemini.api_key", file=sys.stderr)
        sys.exit(2)

    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:
        print("ERROR: missing python package 'openai'. Install with: pip install openai", file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(2)

    client = OpenAI(base_url=base_url, api_key=api_key)

    resp = client.chat.completions.create(
        model=args.model,
        extra_body={"size": args.size},
        messages=[{"role": "user", "content": args.prompt}],
    )

    content = ""
    try:
        content = resp.choices[0].message.content or ""
    except Exception:
        content = ""

    if not content:
        print("ERROR: empty response content; cannot extract image", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    got = try_extract_data_url(content)
    if got:
        fmt, data = got
        # if user provided extension mismatched, keep user choice
        out_path.write_bytes(data)
        print(str(out_path))
        return

    url = try_extract_url(content)
    if url:
        data = download(url)
        out_path.write_bytes(data)
        print(str(out_path))
        return

    b = try_extract_raw_base64(content)
    if b:
        out_path.write_bytes(b)
        print(str(out_path))
        return

    print("ERROR: response did not contain a recognizable image payload.", file=sys.stderr)
    print("--- content (first 800 chars) ---", file=sys.stderr)
    print(content[:800], file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
