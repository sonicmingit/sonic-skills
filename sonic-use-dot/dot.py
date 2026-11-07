#!/usr/bin/env python3
"""Dot. 墨水屏设备控制工具"""
import sys, json, base64, argparse, urllib.request, urllib.error, time
from pathlib import Path
import yaml

CONFIG_PATH = Path.home() / "openclaw" / "secrets.yaml"
BASE_URL = "https://dot.mindreset.tech"

# 🦞 龙虾图标 Base64（40×40 PNG，自动注入纯文本推送）
LOBSTER_ICON_B64 = "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"

# 图片默认参数（实测最优）
DEFAULT_IMAGE_DITHER = "NONE"
DEFAULT_IMAGE_BORDER = 0
def load_dot_config():
    try:
        with open(CONFIG_PATH) as f:
            cfg = yaml.safe_load(f)
        dot = cfg.get("dot") or cfg.get("devices", {}).get("dot", {})
        return dot
    except Exception:
        return {}

def resolve_device(name_or_id):
    dot = load_dot_config()
    api_key = dot.get("api_key")
    if not api_key:
        return None, None, None
    devices = dot.get("devices", [])
    if not name_or_id:
        if devices:
            dev = devices[0]
            return dev.get("device_id"), dev.get("name"), api_key
        dev_id = dot.get("device_id")
        return dev_id, None, api_key
    for dev in devices:
        did = dev.get("device_id", "")
        dname = dev.get("name", "")
        if dname == name_or_id or did == name_or_id:
            return did, dname, api_key
    return None, None, api_key

def api_request(method, path, body=None):
    dot = load_dot_config()
    api_key = dot.get("api_key")
    url = f"{BASE_URL}{path}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        body_str = e.read().decode()
        try:
            return json.loads(body_str), e.code
        except:
            return {"error": body_str}, e.code
    except Exception as e:
        return {"error": str(e)}, 500

def cmd_text(args):
    device_id, device_name, api_key = resolve_device(args.device)
    if not api_key:
        print("错误：未配置 dot.api_key，请检查 secrets.yaml", file=sys.stderr)
        sys.exit(1)
    if not device_id:
        print("错误：未找到设备，请检查 secrets.yaml 中的 devices.dot.devices 配置", file=sys.stderr)
        sys.exit(1)

    body = {"refreshNow": not args.no_refresh}
    if args.title:
        body["title"] = args.title
    if args.message:
        body["message"] = args.message
    if args.signature:
        body["signature"] = args.signature
    else:
        body["signature"] = time.strftime("%y-%m-%d %H:%M")
    if args.link:
        body["link"] = args.link
    if args.task_key:
        body["taskKey"] = args.task_key
    if args.icon:
        icon_path = Path(args.icon).expanduser()
        if not icon_path.exists():
            print(f"错误：图标文件不存在: {icon_path}", file=sys.stderr)
            sys.exit(1)
        with open(icon_path, "rb") as f:
            body["icon"] = base64.b64encode(f.read()).decode()
    else:
        body["icon"] = LOBSTER_ICON_B64

    path = f"/api/authV2/open/device/{device_id}/text"
    result, code = api_request("POST", path, body)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if code != 200:
        sys.exit(1)

def resize_to_png(src_path):
    from PIL import Image
    import io
    img = Image.open(src_path).convert("RGBA")
    img = img.resize((296, 152), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def cmd_image(args):
    device_id, device_name, api_key = resolve_device(args.device)
    if not api_key:
        print("错误：未配置 dot.api_key，请检查 secrets.yaml", file=sys.stderr)
        sys.exit(1)
    if not device_id:
        print("错误：未找到设备，请检查 secrets.yaml 中的 devices.dot.devices 配置", file=sys.stderr)
        sys.exit(1)

    img_path = Path(args.image_path).expanduser()
    if not img_path.exists():
        print(f"错误：图片文件不存在: {img_path}", file=sys.stderr)
        sys.exit(1)

    if img_path.suffix.lower() == ".png":
        with open(img_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()
    else:
        try:
            image_b64 = resize_to_png(img_path)
        except ImportError:
            print("错误：需要 Pillow：pip install Pillow", file=sys.stderr)
            sys.exit(1)

    body = {"image": image_b64, "refreshNow": not args.no_refresh}
    if args.photo:
        body["ditherType"] = "DIFFUSION"
        body["ditherKernel"] = "ATKINSON"
        body["border"] = 0
    else:
        body["ditherType"] = DEFAULT_IMAGE_DITHER
        body["border"] = DEFAULT_IMAGE_BORDER
    if args.link:
        body["link"] = args.link
    if args.border == "white":
        body["border"] = 0
    elif args.border == "black":
        body["border"] = 1
    if args.dither_type:
        body["ditherType"] = args.dither_type.upper()
    if args.dither_kernel:
        body["ditherKernel"] = args.dither_kernel.upper()
    if args.task_key:
        body["taskKey"] = args.task_key

    path = f"/api/authV2/open/device/{device_id}/image"
    result, code = api_request("POST", path, body)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if code != 200:
        sys.exit(1)

def cmd_status(args):
    dot = load_dot_config()
    api_key = dot.get("api_key")
    if not api_key:
        print("错误：未配置 dot.api_key，请检查 secrets.yaml", file=sys.stderr)
        sys.exit(1)

    def print_one(dev_id, dev_name):
        path = f"/api/authV2/open/device/{dev_id}/status"
        result, code = api_request("GET", path)
        if code == 200:
            s = result.get("status", {})
            name = dev_name or dev_id
            print(f"【{name}】")
            print(f"  系统版本：{s.get('version')}")
            print(f"  当前状态：{s.get('current')} — {s.get('description')}")
            print(f"  电池：{s.get('battery')}")
            print(f"  WiFi 信号：{s.get('wifi')}")
            ri = result.get("renderInfo", {})
            print(f"  最后渲染：{ri.get('last') or '无'}")
            n = ri.get("next", {})
            print(f"  下次渲染（电池）：{n.get('battery') or '无'}")
            print(f"  下次渲染（电源）：{n.get('power') or '无'}")
        else:
            print(f"【{dev_name or dev_id}】查询失败：code={code}")

    if args.device:
        device_id, device_name, _ = resolve_device(args.device)
        if not device_id:
            print(f"错误：未找到设备 '{args.device}'", file=sys.stderr)
            sys.exit(1)
        print_one(device_id, device_name)
    else:
        devices = dot.get("devices", [])
        if not devices:
            dev_id = dot.get("device_id")
            if dev_id:
                print_one(dev_id, None)
            else:
                print("错误：未在 secrets.yaml 中找到 dot 设备配置", file=sys.stderr)
                sys.exit(1)
        for dev in devices:
            did = dev.get("device_id")
            dname = dev.get("name")
            print_one(did, dname)

def cmd_list(args):
    dot = load_dot_config()
    api_key = dot.get("api_key")
    if not api_key:
        print("错误：未配置 dot.api_key，请检查 secrets.yaml", file=sys.stderr)
        sys.exit(1)
    task_type = args.task_type or "loop"
    if args.device:
        device_id, device_name, _ = resolve_device(args.device)
        if not device_id:
            print(f"错误：未找到设备 '{args.device}'", file=sys.stderr)
            sys.exit(1)
    else:
        devices = dot.get("devices", [])
        if devices:
            device_id = devices[0].get("device_id")
        else:
            device_id = dot.get("device_id")
        if not device_id:
            print("错误：未找到设备", file=sys.stderr)
            sys.exit(1)
    path = f"/api/authV2/open/device/{device_id}/{task_type}/list"
    result, code = api_request("GET", path)
    if code == 200:
        if isinstance(result, list):
            print(f"共 {len(result)} 条内容：")
            for i, item in enumerate(result, 1):
                print(f"  [{i}] type={item.get('type')}  key={item.get('key')}  refreshNow={item.get('refreshNow')}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Dot. 墨水屏设备控制工具", prog="dot.py")
    sub = parser.add_subparsers(dest="cmd")

    p_text = sub.add_parser("text", help="发送文本到设备")
    p_text.add_argument("-d", "--device", dest="device", help="设备名称或ID（不填默认第一个）")
    p_text.add_argument("-t", "--title", help="标题")
    p_text.add_argument("-m", "--message", help="正文内容（支持 \\n 换行）")
    p_text.add_argument("-s", "--signature", help="署名（不填则自动 yy-mm-dd hh:mm）")
    p_text.add_argument("-i", "--icon", help="图标文件路径（40×40 PNG）；不填自动用 🦞")
    p_text.add_argument("-l", "--link", help="NFC 跳转链接")
    p_text.add_argument("--no-refresh", action="store_true", help="不立即显示")
    p_text.add_argument("--task-key", dest="task_key", help="指定 taskKey")

    p_img = sub.add_parser("image", help="发送图片到设备")
    p_img.add_argument("-d", "--device", dest="device", help="设备名称或ID（不填默认第一个）")
    p_img.add_argument("image_path", help="图片文件路径")
    p_img.add_argument("-l", "--link", help="NFC 跳转链接")
    p_img.add_argument("--border", choices=["white", "black"], help="边框颜色（白/黑）")
    p_img.add_argument("--photo", action="store_true", help="照片模式：Atkinson 抖动；默认 NONE 抖动")
    p_img.add_argument("-d2", "--dither-type", dest="dither_type", choices=["diffusion","ordered","none"], help="抖动类型")
    p_img.add_argument("-k", "--dither-kernel", dest="dither_kernel", help="抖动算法")
    p_img.add_argument("--no-refresh", action="store_true", help="不立即显示")
    p_img.add_argument("--task-key", dest="task_key", help="指定 taskKey")

    p_status = sub.add_parser("status", help="查询设备状态")
    p_status.add_argument("device", nargs="?", help="设备名称或ID（不填查所有）")

    p_list = sub.add_parser("list", help="查询设备内容列表")
    p_list.add_argument("task_type", nargs="?", choices=["loop","fixed"], default="loop", help="内容类型（默认 loop）")
    p_list.add_argument("device", nargs="?", help="设备名称或ID（不填默认第一个）")

    args = parser.parse_args()
    if args.cmd == "text":
        cmd_text(args)
    elif args.cmd == "image":
        cmd_image(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "list":
        cmd_list(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()