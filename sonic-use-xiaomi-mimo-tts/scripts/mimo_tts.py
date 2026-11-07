#!/usr/bin/env python3
import argparse
import base64
import json
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

API_BASE = "https://api.xiaomimimo.com/v1"

# 经验白名单：使用更“像官方标签”的短语，减少被当正文读出来的概率
ALLOWED_AUDIO_TAGS = [
    "紧张，深呼吸",
    "语速加快，碎碎念",
    "小声",
    "极其疲惫，有气无力",
    "长叹一口气",
    "沉默片刻",
    "苦笑",
    "寒冷导致的急促呼吸",
    "咳嗽",
    "提高音量喊话",
    "深呼吸",
    "急促呼吸",
    "有气无力",
    "停顿",
    "喘气",
    "笑着说",
    "哭着说",
    "委屈",
    "可爱",
    "生气",
    "愤怒",
]


def post_json(path: str, payload: dict, api_key: str, timeout: int = 120) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def infer_styles(text: str) -> list[str]:
    t = text.lower()
    styles = []
    if any(k in t for k in ["兴奋", "开心", "庆祝", "激动", "happy"]):
        styles.append("开心")
    if any(k in t for k in ["悲伤", "难过", "低落", "sad"]):
        styles.append("伤感")
    if any(k in t for k in ["严肃", "正式", "通告", "新闻", "serious"]):
        styles.append("正式")
    if any(k in t for k in ["温柔", "睡前", "轻声", "whisper"]):
        styles.append("轻声")
    if any(k in t for k in ["愤怒", "生气", "怒", "angry"]):
        styles.append("愤怒")
    return styles


def _normalize_tag_text(s: str) -> str:
    return re.sub(r"\s+", "", s.strip().strip("（）()"))


def _pick_allowed_tag(raw: str) -> str | None:
    x = _normalize_tag_text(raw)
    if not x:
        return None
    # 完全命中优先
    for t in ALLOWED_AUDIO_TAGS:
        if x == _normalize_tag_text(t):
            return t
    # 包含命中次之
    for t in ALLOWED_AUDIO_TAGS:
        if _normalize_tag_text(t) in x or x in _normalize_tag_text(t):
            return t
    return None


def sanitize_inline_audio_tags(text: str) -> str:
    """清理文案里的括号标签：未知标签直接移除，避免被当正文读出来。"""
    def repl(m):
        raw = m.group(1)
        ok = _pick_allowed_tag(raw)
        return f"（{ok}）" if ok else ""

    # 统一处理全角/半角括号
    text = re.sub(r"（([^（）]{1,30})）", repl, text)
    text = re.sub(r"\(([^()]{1,30})\)", repl, text)
    return text


def build_styled_text(raw_text: str, styles: list[str], audio_tags: list[str]) -> str:
    # MiMo style control: <style>风格1 风格2</style>放在文本开头
    style_words = [s.strip() for s in styles if s.strip()]
    style_prefix = f"<style>{' '.join(style_words)}</style>" if style_words else ""

    # CLI 传入的标签：只保留白名单可识别项
    bracket_tags = []
    for t in audio_tags:
        x = t.strip()
        if not x:
            continue
        chosen = _pick_allowed_tag(x)
        if chosen:
            bracket_tags.append(f"（{chosen}）")

    tag_prefix = "".join(bracket_tags)
    merged = "".join([x for x in [style_prefix, tag_prefix, raw_text.strip()] if x])
    return sanitize_inline_audio_tags(merged.strip())


def generate_text_from_brief(brief: str, api_key: str) -> str:
    prompt = (
        "你是高级TTS导演，请生成一段可直接给小米MiMo TTS使用的口播文本。"
        "要求：\n"
        "1) 只输出最终可合成文本，不要解释。\n"
        "2) 必须在开头使用 <style>...</style>，多风格写在同一个标签里。\n"
        "3) 强化细粒度情绪标签：全篇按节奏分段插入括号标签，例如"
        "（紧张，深呼吸）（沉默片刻）（提高音量喊话）（语速加快，碎碎念）"
        "（极其疲惫，有气无力）（苦笑）（咳嗽）（小声）（长叹一口气）等。\n"
        "4) 标签密度要明显高于普通文案：建议每1~2句至少1个标签，关键情绪转折处必须有标签。\n"
        "5) 追求拟人化与情绪层次：至少包含3次以上情绪/语气变化（如平静->兴奋->收束）。\n"
        "6) 保持可听性，不机械堆标签；内容长度控制在120~260字。\n"
        "7) 若是唱歌场景，必须用 <style>唱歌</style> 放在文本最前。\n"
        f"\n用户需求：{brief}"
    )
    payload = {
        "model": "mimo-v2-pro",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "top_p": 0.9,
    }
    data = post_json("/chat/completions", payload, api_key)
    return data["choices"][0]["message"]["content"].strip()


def enrich_emotion_tags_if_needed(text: str, brief: str, api_key: str, min_tags: int = 5) -> str:
    """若生成文本的括号情绪标签过少，自动做一次增强改写。"""
    tag_count = text.count("（")
    if tag_count >= min_tags:
        return text

    prompt = (
        "请把下面这段小米TTS文本改写为更强情绪颗粒度版本。"
        "只输出改写后的最终文本。"
        "硬性要求：\n"
        "1) 保留开头<style>标签。\n"
        "2) 全文插入至少5个括号标签，且分布均匀。\n"
        "3) 标签尽量多样化，至少覆盖：呼吸/停顿/语速变化/音量变化/微情绪。\n"
        "4) 不改变核心语义。\n"
        f"\n原始需求：{brief}\n"
        f"\n待改写文本：{text}"
    )
    payload = {
        "model": "mimo-v2-pro",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "top_p": 0.95,
    }
    data = post_json("/chat/completions", payload, api_key)
    return data["choices"][0]["message"]["content"].strip()


def synthesize(text: str, user_context: str, voice: str, out_format: str, api_key: str, temperature: float) -> tuple[bytes, dict]:
    msgs = []
    if user_context:
        msgs.append({"role": "user", "content": user_context})
    msgs.append({"role": "assistant", "content": text})

    payload = {
        "model": "mimo-v2-tts",
        "messages": msgs,
        "audio": {"format": out_format, "voice": voice},
        "temperature": temperature,
    }
    data = post_json("/chat/completions", payload, api_key)
    audio_b64 = data["choices"][0]["message"]["audio"]["data"]
    return base64.b64decode(audio_b64), data


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout


def can_local_encode_amr() -> bool:
    code, out = run_cmd(["ffmpeg", "-hide_banner", "-encoders"])
    if code != 0:
        return False
    return ("libopencore_amrnb" in out) or (" amr_nb" in out)


def convert_to_amr(input_audio: str, output_amr: str, docker_image: str = "jrottenberg/ffmpeg:6.1-ubuntu") -> dict:
    src = str(Path(input_audio).resolve())
    dst = str(Path(output_amr).resolve())
    Path(dst).parent.mkdir(parents=True, exist_ok=True)

    # 1) try local ffmpeg first
    if can_local_encode_amr():
        local_cmd = [
            "ffmpeg", "-y", "-i", src,
            "-ar", "8000", "-ac", "1", "-b:a", "12.2k",
            "-c:a", "libopencore_amrnb", dst,
        ]
        code, out = run_cmd(local_cmd)
        if code == 0:
            return {"ok": True, "method": "local-ffmpeg", "log": out}

    # 2) fallback to docker ffmpeg with libopencore_amrnb
    mount_dir = str(Path(src).parent)
    in_name = Path(src).name
    out_name = Path(dst).name
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{mount_dir}:/work",
        docker_image,
        "-y", "-i", f"/work/{in_name}",
        "-ar", "8000", "-ac", "1", "-b:a", "12.2k",
        "-c:a", "libopencore_amrnb", f"/work/{out_name}",
    ]
    code, out = run_cmd(docker_cmd)
    if code == 0 and Path(dst).exists():
        return {"ok": True, "method": "docker-ffmpeg", "log": out, "docker_image": docker_image}

    return {
        "ok": False,
        "method": "docker-ffmpeg",
        "log": out,
        "cmd": " ".join(shlex.quote(x) for x in docker_cmd),
    }


def main():
    p = argparse.ArgumentParser(description="Xiaomi MiMo TTS helper")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Raw text to synthesize")
    src.add_argument("--brief", help="Generate TTS text from a rough brief first")

    p.add_argument("--voice", default="mimo_default", choices=["mimo_default", "default_zh", "default_en"])
    p.add_argument("--format", default="wav", choices=["wav", "mp3", "pcm"])
    p.add_argument("--style", action="append", default=[], help="Style words, can be repeated")
    p.add_argument("--tag", action="append", default=[], help="细粒度语气标签，会转成括号格式，如 紧张，深呼吸")
    p.add_argument("--auto-style", action="store_true", help="Infer style words from text")
    p.add_argument("--user-context", default="", help="Optional user role context")
    p.add_argument("--temperature", type=float, default=0.6)
    p.add_argument("--api-key", default=os.environ.get("MIMO_API_KEY", ""))
    p.add_argument("--out", default="", help="Output file path")
    p.add_argument("--to-amr", action="store_true", help="Convert output audio to AMR (8k mono) for voice-message channels")
    p.add_argument("--docker-image", default="jrottenberg/ffmpeg:6.1-ubuntu", help="ffmpeg docker image for AMR fallback")
    p.add_argument("--print-text", action="store_true", help="Print final synthesized text")

    args = p.parse_args()
    if not args.api_key:
        print("ERROR: Missing API key. Set MIMO_API_KEY or pass --api-key", file=sys.stderr)
        sys.exit(2)

    if args.brief:
        raw_text = generate_text_from_brief(args.brief, args.api_key)
        raw_text = enrich_emotion_tags_if_needed(raw_text, args.brief, args.api_key)
    else:
        raw_text = args.text

    # 对文案里的括号标签做一次清理，尽量避免“标签被朗读”
    raw_text = sanitize_inline_audio_tags(raw_text)

    styles = list(args.style)
    if args.auto_style:
        styles.extend([s for s in infer_styles(raw_text) if s not in styles])

    final_text = build_styled_text(raw_text, styles, args.tag)
    if args.print_text:
        print(final_text)

    audio, raw_resp = synthesize(
        text=final_text,
        user_context=args.user_context,
        voice=args.voice,
        out_format=args.format,
        api_key=args.api_key,
        temperature=args.temperature,
    )

    default_dir = os.path.expanduser("~/.openclaw/audio")
    os.makedirs(default_dir, exist_ok=True)
    out = args.out or os.path.join(default_dir, f"mimo_tts_{int(time.time())}.{args.format}")
    with open(out, "wb") as f:
        f.write(audio)

    # 保存发送给 TTS API 的最终文本，便于回溯核验
    text_out = str(Path(out).with_suffix(".txt"))
    with open(text_out, "w", encoding="utf-8") as f:
        f.write(final_text)

    amr_out = ""
    amr_info = None
    if args.to_amr:
        amr_out = str(Path(out).with_suffix(".amr"))
        amr_info = convert_to_amr(out, amr_out, docker_image=args.docker_image)
        if not amr_info.get("ok"):
            print(json.dumps({"error": "AMR convert failed", **amr_info}, ensure_ascii=False, indent=2), file=sys.stderr)
            sys.exit(3)

    result = {
        "output": out,
        "text_output": text_out,
        "bytes": len(audio),
        "voice": args.voice,
        "format": args.format,
        "final_text": final_text,
        "has_user_context": bool(args.user_context),
        "model": raw_resp.get("model"),
        "amr_output": amr_out or None,
        "amr_info": amr_info,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
