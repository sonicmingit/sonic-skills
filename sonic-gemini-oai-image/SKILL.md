---
name: sonic-gemini-oai-image
description: 通过兼容OpenAI的API生成图片，该API提供Gemini图片模型（如model=gemini-3-pro-image），支持可配置的base_url。当用户想生成图片但更喜欢使用自己的base_url/代理和存储在~/openclaw/secrets.yaml中models.1821gemini下的密钥时使用。
---

# sonic-gemini-oai-image

Generate images through an **OpenAI-compatible** endpoint (e.g. `http://<host>:8045/v1`) that exposes a Gemini image model like `gemini-3-pro-image`.

## Key / base_url source (local)

This skill expects credentials in **local secrets** (do not paste keys in chat):

- `~/openclaw/secrets.yaml`
  - `models.1821gemini.base_url`  (example: `http://10.0.1.30:8045/v1`)
  - `models.1821gemini.api_key`   (example: `sk-...`)

You can override with flags.

## Generate an image

```bash
uv run --with openai --with pyyaml \
  /home/sonic/.openclaw/skills/sonic-gemini-oai-image/scripts/generate_image.py \
  --prompt "一群小龙虾在办公室协作工作，温暖灯光，可爱3D风格" \
  --size 1024x1024 \
  --out /tmp/openclaw/crayfish.png
```

## Common options

- `--model gemini-3-pro-image` (default)
- `--base-url http://10.0.1.30:8045/v1` (default from secrets)
- `--api-key sk-...` (default from secrets; avoid passing in shell history)
- `--size 1024x1024` (also supports 1280x720 / 720x1280 / 1216x896 depending on your gateway)

## Notes

- Script is defensive about response formats:
  - If the server returns a **data URL** or **base64**, it will decode and write `--out`.
  - If the server returns an **http(s) URL** in the content, it will download.
  - If the response is pure text without image payload, it will print the content and exit non-zero.
