#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MiniMax Image Generation (T2I/I2I)

Defaults:
- secrets: ~/openclaw/secrets.yaml
  - models.minimax.base_url e.g. https://api.minimaxi.com
  - models.minimax.api_key

Note: This skill follows 方案B: base_url includes /v1 and we call {base_url}/image_generation.

Writes the first returned image to --out.
"""

import argparse
import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import yaml


def load_secrets() -> Dict[str, Any]:
    p = Path(os.path.expanduser("~/openclaw/secrets.yaml"))
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def infer_ext_from_out(out_path: str, default_ext: str) -> str:
    ext = Path(out_path).suffix.lower().lstrip(".")
    if ext:
        return ext
    return default_ext


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--model", default="image-01")
    ap.add_argument("--aspect-ratio", default="1:1")
    ap.add_argument("--response-format", default="base64", choices=["base64"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--api-key", default=None)

    # optional I2I
    ap.add_argument("--ref-image-url", default=None)
    ap.add_argument("--ref-type", default="character", choices=["character", "style", "subject"])

    args = ap.parse_args()

    secrets = load_secrets()
    mm = ((secrets.get("models") or {}).get("minimax") or {}) if isinstance(secrets, dict) else {}

    base_url = (args.base_url or mm.get("base_url") or "").rstrip("/")
    api_key = args.api_key or mm.get("api_key")

    if not base_url:
        raise SystemExit("Missing base_url. Set models.minimax.base_url in ~/openclaw/secrets.yaml")
    if not api_key:
        raise SystemExit("Missing api_key. Set models.minimax.api_key in ~/openclaw/secrets.yaml")

    url = f"{base_url}/image_generation"

    payload: Dict[str, Any] = {
        "model": args.model,
        "prompt": args.prompt,
        "aspect_ratio": args.aspect_ratio,
        "response_format": args.response_format,
    }

    if args.ref_image_url:
        payload["subject_reference"] = [
            {"type": args.ref_type, "image_file": args.ref_image_url}
        ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    r = requests.post(url, headers=headers, json=payload, timeout=args.timeout)
    # Avoid printing secrets; ok to print limited error context
    if r.status_code != 200:
        raise SystemExit(f"HTTP {r.status_code}: {r.text[:1000]}")

    j = r.json()
    images = (((j.get("data") or {}).get("image_base64")) if isinstance(j, dict) else None)
    if not images or not isinstance(images, list) or not images[0]:
        raise SystemExit(f"No image_base64 found in response: {json.dumps(j, ensure_ascii=False)[:2000]}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine extension
    ext = infer_ext_from_out(str(out_path), "jpg")
    if out_path.suffix == "":
        out_path = out_path.with_suffix("." + ext)

    out_path.write_bytes(base64.b64decode(images[0]))

    meta = {
        "request": {k: payload.get(k) for k in ["model", "prompt", "aspect_ratio", "response_format"]},
        "endpoint": url,
        "out": str(out_path),
        "id": j.get("id") if isinstance(j, dict) else None,
    }
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
