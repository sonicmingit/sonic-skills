# Xiaomi MiMo TTS API Notes

Source: Xiaomi MiMo Open Platform docs (content extracted from platform bundle on 2026-03-19).

## Endpoint
- `POST https://api.xiaomimimo.com/v1/chat/completions`

## Auth
- Header either:
  - `api-key: $MIMO_API_KEY`
  - `Authorization: Bearer $MIMO_API_KEY`

## Required model
- `model: "mimo-v2-tts"` for speech synthesis.

## Messages rule (important)
- To synthesize speech, target text should be in a message with:
  - `role: "assistant"`
- `role: "user"` message is optional context.

## Audio object
- `audio.format`: `wav` | `mp3` | `pcm`
- `audio.voice`: `mimo_default` | `default_zh` | `default_en`

## 风格 / 标签控制
- 风格控制使用：`<style>风格1 风格2</style>`，并放在目标文本最开头。
- 细粒度控制推荐括号标签：`（紧张，深呼吸）`、`（沉默片刻）`、`（提高音量喊话）` 等。
- 支持唱歌风格：必须在文本最开头放置 `<style>唱歌</style>`。

## Typical response path
- Base64 audio data at:
  - `choices[0].message.audio.data`
- Decode and write to file.

## Example request skeleton
```json
{
  "model": "mimo-v2-tts",
  "messages": [
    {"role": "user", "content": "optional context"},
    {"role": "assistant", "content": "开心 [cough] 这里是要合成的文本"}
  ],
  "audio": {
    "format": "wav",
    "voice": "mimo_default"
  }
}
```
