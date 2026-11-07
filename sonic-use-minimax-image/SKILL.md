---
name: sonic-use-MiniMax图片生成
description: 通过 MiniMax 开放平台 Image Generation API（/image_generation）进行文生图/图生图。默认从 ~/openclaw/secrets.yaml 读取 models.minimax.base_url(需包含/v1) 与 models.minimax.api_key。
---

# sonic-use-MiniMax图片生成

用于调用 **MiniMax 图片生成**（文生图 / 图生图）。

## 约定（方案 B）

- `~/openclaw/secrets.yaml`
  - `models.minimax.base_url`: **必须包含** `/v1`，例如：`https://api.minimaxi.com/v1`
  - `models.minimax.api_key`: `Bearer` token

因此脚本内固定拼接：`{base_url}/image_generation`（不会再加 `/v1`）。

## 文生图（最常用）

```bash
python3 /home/sonic/.openclaw/skills/sonic-use-minimax-image/scripts/generate.py \
  --prompt "一只红色小龙虾的极简扁平图标，白底" \
  --aspect-ratio 1:1 \
  --out /tmp/openclaw/minimax.png
```

## 图生图（参考图/角色一致性）

```bash
python3 /home/sonic/.openclaw/skills/sonic-use-minimax-image/scripts/generate.py \
  --prompt "女孩在图书馆的窗户前，看向远方" \
  --aspect-ratio 16:9 \
  --ref-image-url "https://example.com/character.jpg" \
  --ref-type character \
  --out /tmp/openclaw/minimax-i2i.jpg
```

## 常用参数

- `--model`：默认 `image-01`
- `--aspect-ratio`：默认 `1:1`（可用如 `16:9`, `9:16`, `4:3` 等）
- `--timeout`：默认 120 秒
- `--base-url/--api-key`：可覆盖 secrets（不建议在命令行明文传 key）

## 返回

- 成功时把图片写入 `--out`
- 同时输出 JSON 元信息到 stdout（不包含 key）
