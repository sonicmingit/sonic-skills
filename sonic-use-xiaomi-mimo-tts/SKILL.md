---
name: sonic-use-小米MiMo语音
description: 使用小米 MiMo TTS（mimo-v2-tts）生成语音并发送文件。适用于：用户要把文本转语音、要根据大意自动生成带风格/音频标签的朗读稿、或要开启“语音模式”（后续回复自动转语音发送）。
---

# sonic-use-小米MiMo语音

使用小米 MiMo Open Platform 的 `mimo-v2-tts` 做语音合成，支持 `<style>...</style>` 风格控制与括号细粒度语气标签。

## 快速规则

1. API 端点：`POST https://api.xiaomimimo.com/v1/chat/completions`
2. 合成文本必须放在 `messages` 的 `role: assistant` 里。
3. 使用 `audio` 指定输出：
   - `format`: `wav|mp3|pcm`
   - `voice`: `mimo_default|default_zh|default_en`
4. 风格控制：必须在文本最开头使用 `<style>风格1 风格2</style>`（多风格放同一个标签内）。
5. 细粒度控制：使用括号标签，如 `（紧张，深呼吸）`、`（沉默片刻）`、`（提高音量喊话）`。

详见 `references/api-notes.md`。

## 三种工作模式

### 1) 大意 -> 自动生成可朗读文案 -> 合成语音

当用户只给主题/场景时，先生成带 `<style>...</style>` 和括号标签的合成文本，再 TTS。该模式会自动增强情绪标签密度（标签偏少时自动二次改写）。

```bash
python3 scripts/mimo_tts.py \
  --brief "做一个20秒开场白，科技感、兴奋一点" \
  --voice mimo_default \
  --format wav \
  --out ~/.openclaw/audio/mimo_intro.wav \
  --print-text
```

完成后在回复里发送：

```text
MEDIA: ~/.openclaw/audio/mimo_intro.wav
```

### 2) 用户给定文本 -> 直接合成

```bash
python3 scripts/mimo_tts.py \
  --text "<style>悄悄话</style>（轻咳）今天我们来讲三个要点。" \
  --voice default_zh \
  --format wav \
  --out ~/.openclaw/audio/mimo_text.wav
```

如果用户没指定风格，可用 `--auto-style` 自动补风格词：

```bash
python3 scripts/mimo_tts.py --text "明天上线，大家辛苦了！" --auto-style --out ~/.openclaw/audio/mimo_auto.wav
```

### 3) 语音模式（后续每次回复自动转语音）

实现方式（会话级约定）：
1. 用户说“开启语音模式”后，后续先生成文本回复。
2. 用该文本调用 `scripts/mimo_tts.py --text ...` 合成。
3. 回复时附带 `MEDIA: <音频路径>`。
4. 用户说“关闭语音模式”后恢复普通文本。

建议状态文件（可选）：`~/.openclaw/mimo-voice-mode.json`

## 脚本

- `scripts/mimo_tts.py`
  - `--brief`：先用 `mimo-v2-pro` 生成可合成文案，再TTS
  - `--text`：直接合成用户文本
  - `--style/--tag`：追加风格与细粒度标签（最终会生成 `<style>...</style>` 与 `（...）` 格式）
  - `--auto-style`：按文本语义自动补风格词
  - `--voice/--format`：语音参数
  - `--to-amr`：自动转 AMR（8k 单声道）
  - `--out`：输出文件路径

## 注意事项

- 依赖环境变量：`MIMO_API_KEY`
- 默认输出目录已改为 `~/.openclaw/audio/`（可用 `--out` 覆盖）。
- 每次合成会自动把“发给 API 的最终文本”按同名 `.txt` 落盘（与音频同目录），便于核验。
- 语音消息形态推荐 AMR：可使用 `--to-amr`。脚本会优先本机 ffmpeg 编码，失败时自动回退 docker ffmpeg（`jrottenberg/ffmpeg:6.1-ubuntu`）。
- 细粒度标签建议多样化组合：`（紧张，深呼吸）`、`（沉默片刻）`、`（提高音量喊话）`、`（语速加快，碎碎念）`、`（小声）`、`（长叹一口气）`、`（苦笑）`、`（咳嗽）`。
- 脚本会自动清洗括号标签：非白名单标签会被移除，减少“标签被直接朗读”的情况。
- 唱歌场景需把 `<style>唱歌</style>` 放在目标文本最前面。
