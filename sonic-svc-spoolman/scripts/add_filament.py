#!/usr/bin/env python3
# sonic-svc-spoolman - 添加新耗材/线轴记录
# 用法: python3 add_filament.py --brand "点维" --name "哑光苏军绿" --material "PETG" --color "哑光苏军绿" --price 18 --location "拼多多"

import json
import sys
import os
import argparse
import urllib.request
import urllib.error
from datetime import datetime

# ============ 配置 ============
BASE_URL = "http://10.0.1.30:7910"
COLORS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "colors.json")
TYPES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "filament_types.json")
BRANDS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "brand_mapping.json")

# ============ 扩展颜色映射（colors.json 补充） ============
# 注意：key 越精确越长越优先，模糊匹配按顺序进行
EXTRA_COLORS = {
    # 精确颜色名（越长越优先匹配）
    "哑光苏军绿": "#4B5320",
    "丝绸苏军绿": "#4B5320",
    "苏军绿": "#4B5320",
    "银河宝石蓝": "#4169E1",
    "极光蓝": "#00BFFF",
    "冰晶蓝": "#B0E0E6",
    "马卡龙蓝": "#A2C2E0",
    "樱花粉": "#FADADD",
    "玫瑰金": "#B76E79",
    "抹茶绿": "#A3C9A8",
    "莫兰迪绿": "#8F9D8B",
    "莫兰迪蓝": "#7B9DBA",
    "莫兰迪灰": "#A9A9A9",
    "莫兰迪粉": "#D4A5A5",
    "莫兰迪紫": "#B4A7C7",
    "奶茶色": "#D2B48C",
    "奶咖色": "#C4A484",
    "焦糖色": "#8B4513",
    "琥珀色": "#FFBF00",
    "蜜瓜绿": "#93C572",
    "活力橙": "#FF8C00",
    "珊瑚橙": "#FF7F50",
    "香芋紫": "#DA70D6",
    "雾霾紫": "#9B7FA6",
    "薰衣草": "#E6E6FA",
    "冰川蓝": "#AFEEEE",
    "湖水蓝": "#20B2AA",
    "深空蓝": "#191970",
    "星空紫": "#483D8B",
    "幻影灰": "#C0C0C0",
    "钢琴黑": "#0D0D0D",
    "日落橙": "#FD5E53",
    "苹果绿": "#8DB600",
    "翡翠绿": "#50C878",
    "鼠尾草绿": "#8F9D8B",
    "蓝灰": "#64748B",
    "天青蓝": "#007FFF",
    "普鲁士蓝": "#003153",
    "电光紫": "#8B00FF",
    "幻彩紫": "#9B59B6",
    "糖果粉": "#FF69B4",
    "蜜桃粉": "#FFCBA4",
    "人鱼姬": "#F7CAC9",
    "贝壳粉": "#FFE4E1",
    "草莓粉": "#FC5A8D",
    "西瓜红": "#FF6B6B",
    "石榴红": "#E25822",
    "复古红": "#C41E3A",
    "铁锈红": "#B7410E",
    "珊瑚红": "#FF6F61",
    "可可棕": "#D2691E",
    "摩卡棕": "#6F4E37",
    "焦糖棕": "#A0522D",
    "红棕": "#964B00",
    "朱古力": "#7B3F00",
    "杏黄": "#FFAF60",
    "霓虹绿": "#39FF14",
    "松石绿": "#40E0D0",
    "绿松石": "#40E0D0",
    "翠绿": "#00FA9A",
    "墨绿": "#014421",
    "朱砂红": "#8B0000",
    "酱红色": "#800000",
    "中国红": "#DE2910",
    "正红": "#FF0000",
    "胭脂红": "#DC143C",
    "桔红": "#FF2400",
    "芒果黄": "#FF8243",
    "蛋黄色": "#FFD700",
    "秋香色": "#808000",
    "卯石色": "#BC8F8F",
    "藕荷色": "#C9A9C9",
    "藤色": "#C9A9C9",
    "栗棕色": "#781F16",
    "梨黄": "#C8A84B",
    "烟灰蓝": "#708090",
    "雾霾蓝": "#98AFC7",
    "牛油果绿": "#9DC183",
    "古铜色": "#8B4513",
    "苔藓绿": "#8A9A5B",
    "宇宙蓝": "#003366",
    "海洋蓝": "#006994",
    "钴蓝": "#0047AB",
    "藏青": "#1B3A5F",
    "靛蓝": "#4B0082",
    "烟紫": "#9370DB",
    "西柚粉": "#FFC0CB",
    "可可棕": "#D2691E",
    # 短颜色名（用于模糊兜底，越靠后越不精确）
    "苏军绿": "#4B5320",
    "军绿色": "#4B5320",
    "暗夜绿": "#3D4B3D",
    "琥珀": "#FFBF00",
    "焦糖": "#8B4513",
    "摩卡": "#6F4E37",
    "翡翠": "#50C878",
    "墨绿": "#014421",
    "雪白": "#FFFAFA",
    "纯白": "#FFFFFF",
    "纯黑": "#000000",
    "象牙白": "#FFFFF0",
    "米白": "#F5F5DC",
    "月白": "#E8F0F5",
    "浅粉": "#FADADD",
    "浅橙": "#FFDAB9",
    "浅黄": "#FFFFE0",
    "浅绿": "#90EE90",
    "浅蓝": "#ADD8E6",
    "浅紫": "#E6E6FA",
    "浅棕": "#A52A2A",
    "浅灰": "#D3D3D3",
    "深灰": "#696969",
    "深紫": "#663399",
    "深绿": "#006400",
    "深黄": "#B8860B",
    "深棕": "#5C4033",
    "深红": "#8B0000",
    "深橙": "#FF8C00",
    "深粉": "#FF1493",
    "暗红": "#8B0000",
    "暗绿": "#006400",
    "暗蓝": "#00008B",
    "暗紫": "#663399",
    "暗灰": "#696969",
    "暗黄": "#B8860B",
    "暗棕": "#5C4033",
    "暗橙": "#FF8C00",
    "暗粉": "#FF1493",
}

# ============ 工具函数 ============
def load_colors():
    """加载颜色映射表"""
    try:
        with open(COLORS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"WARNING: 无法加载颜色文件: {e}", file=sys.stderr)
        return {}

def load_filament_types():
    """加载耗材类型映射表"""
    try:
        with open(TYPES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"WARNING: 无法加载耗材类型文件: {e}", file=sys.stderr)
        return {}

def load_brands():
    """加载品牌映射表"""
    try:
        with open(BRANDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"WARNING: 无法加载品牌映射文件: {e}", file=sys.stderr)
        return {}

def resolve_brand(brand_input):
    """解析品牌名称，支持映射"""
    brands_map = load_brands()
    if brand_input in brands_map:
        resolved = brands_map[brand_input]
        print(f"🏭 品牌映射: '{brand_input}' -> '{resolved}'")
        return resolved
    return brand_input

def resolve_filament_type(name, material_hint):
    """解析耗材类型（材料+表面处理），映射为英文"""
    types_map = load_filament_types()
    
    if not name:
        return material_hint
    
    name_lower = name.lower()
    
    # 1. 先在 types_map 中精确匹配
    sorted_keys = sorted(types_map.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key in name_lower:
            resolved = types_map[key]
            print(f"🔧 耗材类型映射: '{name}' -> '{resolved}'")
            return resolved
    
    # 2. 从名称中提取材料类型
    material_keywords = {
        "petg": "PETG", "pla": "PLA", "abs": "ABS", "tpu": "TPU",
        "尼龙": "Nylon", "nylon": "Nylon", "asa": "ASA", "pc": "PC",
    }
    base_material = "PLA"
    for kw, mat in material_keywords.items():
        if kw in name_lower:
            base_material = mat
            break
    
    # 3. 提取表面处理
    finish = ""
    finish_map = {
        "哑光": "Matte", "磨砂": "Matte",
        "丝绸": "Silk", "丝滑": "Silk", "闪丝": "Silk",
        "丝绒": "Velvet",
        "珠光": "Pearl",
        "透明": "Translucent",
        "韧性+": "Tough+", "韧性": "Tough",
        "高速": "HF",
        "碳纤": "CF",
        "金属": "Metal",
        "基本": "Basic",
    }
    for kw, f in finish_map.items():
        if kw in name_lower:
            finish = f
            break
    
    result = f"{base_material} {finish}" if finish else base_material
    print(f"🔧 材料类型解析: '{name}' -> '{result}'")
    return result

def color_to_hex(color_name, colors_map):
    """将颜色名称转换为 HEX 值
    
    查找顺序：
    1. 精确匹配 EXTRA_COLORS（优先，因为更精确）
    2. 精确匹配 colors_map（忽略大小写）
    3. 模糊匹配 EXTRA_COLORS
    4. 模糊匹配 colors_map（包含关系）
    5. 视为 HEX 值（以 # 开头）
    6. 返回 (None, original_name)
    """
    if not color_name:
        return None, color_name
    
    color_name = color_name.strip()
    original_name = color_name
    color_lower = color_name.lower()
    
    # 1. 精确匹配 EXTRA_COLORS
    if color_lower in EXTRA_COLORS and EXTRA_COLORS[color_lower] is not None:
        return EXTRA_COLORS[color_lower].upper(), color_name
    
    # 2. 精确匹配 colors_map（忽略大小写）
    for name_key, hex_val in colors_map.items():
        if name_key.lower() == color_lower:
            return hex_val.upper(), color_name
    
    # 3. 模糊匹配 EXTRA_COLORS（颜色名包含关键词，且 EXTRA_COLORS 中的 key 更短或相等）
    for name_key, hex_val in EXTRA_COLORS.items():
        if hex_val is None:
            continue
        # 只有当 EXTRA_COLORS 中的颜色名是 color_name 的子串时才匹配
        # 避免 "军绿色" 错误匹配到 "哑光苏军绿"
        if name_key in color_name:
            return hex_val.upper(), color_name
    
    # 4. 模糊匹配 colors_map（包含关系，且 key 是 color_name 的子串优先）
    for name_key, hex_val in colors_map.items():
        if name_key in color_name and len(name_key) >= 2:
            return hex_val.upper(), color_name
    
    # 5. 已经是 HEX 值
    if color_name.startswith("#") and len(color_name) in [4, 7]:
        return color_name.upper(), color_name
    
    # 6. 未找到
    return None, original_name

def extract_color_name(name, colors_map):
    """从耗材名称中提取纯颜色名（去掉材料前缀）
    
    规则：
    - 如果名称中含颜色，从材料名后开始截取
    - 保留表面处理描述（如"哑光"）+ 颜色名
    - 例如 "PETG哑光苏军绿" -> "哑光苏军绿"
    """
    if not name:
        return name
    
    # 材料前缀列表
    mat_prefixes = ["PETG", "PLA", "ABS", "TPU", "Nylon", "ASA", "PC", "PVA", "BVOH"]
    mat_prefixes_lower = [p.lower() for p in mat_prefixes]
    
    # 表面处理关键词
    finish_patterns = ["哑光", "磨砂", "丝绸", "丝滑", "闪丝", "丝绒", "珠光", "透明"]
    
    # 合并所有颜色映射
    all_colors = dict(colors_map)
    for k, v in EXTRA_COLORS.items():
        if v is not None:
            all_colors[k] = v
    
    # 优先匹配已知颜色名（从长到短）
    color_candidates = []
    for color_key in all_colors.keys():
        if color_key and len(color_key) >= 2 and color_key.strip() not in finish_patterns:
            if color_key in name:
                color_candidates.append(color_key)
    
    color_candidates.sort(key=len, reverse=True)
    
    if color_candidates:
        matched = color_candidates[0]
        idx = name.index(matched)
        before = name[:idx].strip()
        after = name[idx + len(matched):].strip()
        
        # 去掉材料前缀
        before_lower = before.lower()
        prefix_removed = False
        for p, p_lower in zip(mat_prefixes, mat_prefixes_lower):
            if before == p or before_lower == p_lower:
                before = ""
                prefix_removed = True
                break
            if before_lower.startswith(p_lower + " ") or before_lower.startswith(p_lower + "-"):
                before = before[len(p):].strip()
                prefix_removed = True
                break
        
        result = f"{before}{matched}{after}".strip()
        result = result.replace("--", "-").replace(" - ", "-").replace(" ", "")
        
        # 如果结果不以表面处理词开头且 before 被去掉了，补上
        has_finish = any(fp in name for fp in finish_patterns)
        if has_finish and not any(result.startswith(fp) for fp in finish_patterns):
            for fp in finish_patterns:
                if fp in name and fp not in result:
                    result = fp + result
                    break
        
        return result if result else name
    
    # 如果没匹配到已知颜色，提取"哑光"等描述 + 剩余部分
    finish_extracted = ""
    remaining = name
    for fp in finish_patterns:
        if fp in remaining:
            finish_extracted = fp
            remaining = remaining.replace(fp, "").strip()
            break
    
    for p, p_lower in zip(mat_prefixes, mat_prefixes_lower):
        if remaining.startswith(p) or remaining.lower().startswith(p_lower):
            remaining = remaining[len(p):].strip()
            break
        if remaining.endswith(p) or remaining.lower().endswith(p_lower):
            remaining = remaining[:-len(p)].strip()
            break
    
    remaining = remaining.strip(" -_").strip()
    
    if finish_extracted and remaining:
        return f"{finish_extracted}{remaining}"
    elif remaining:
        return remaining
    elif finish_extracted:
        return finish_extracted
    else:
        return name

def api_request(method, path, data=None):
    """发送 API 请求"""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    
    try:
        if method == "GET":
            req = urllib.request.Request(url, headers=headers, method="GET")
        elif method == "POST":
            req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode(), method="POST")
        elif method == "PUT":
            req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode(), method="PUT")
        elif method == "DELETE":
            req = urllib.request.Request(url, headers=headers, method="DELETE")
        else:
            raise ValueError(f"不支持的 HTTP 方法: {method}")
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_data = resp.read().decode()
            if resp_data:
                return json.loads(resp_data)
            return {"success": True, "data": None}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        try:
            error_json = json.loads(error_body) if error_body else {}
            return {"success": False, "message": error_json.get("message", str(e)), "data": None}
        except:
            return {"success": False, "message": f"HTTP {e.code}: {error_body[:200]}", "data": None}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def find_or_create_vendor(brand_name):
    """查找或创建供应商"""
    result = api_request("GET", f"/api/v1/vendors?name={urllib.request.quote(brand_name)}")
    
    if result.get("success") and result.get("data"):
        vendors = result["data"]
        if isinstance(vendors, list) and len(vendors) > 0:
            for v in vendors:
                if v.get("name") == brand_name:
                    print(f"✅ 找到供应商: {v['name']} (ID: {v['id']})")
                    return v["id"]
    
    print(f"📦 供应商 '{brand_name}' 不存在，正在创建...")
    result = api_request("POST", "/api/v1/vendors", {"name": brand_name})
    
    if result.get("success"):
        vendor_id = result["data"]["id"]
        print(f"✅ 供应商创建成功: {brand_name} (ID: {vendor_id})")
        return vendor_id
    else:
        raise Exception(f"创建供应商失败: {result.get('message')}")

def find_filament(name, vendor_id):
    """查找耗材"""
    result = api_request("GET", f"/api/v1/filaments?name={urllib.request.quote(name)}&vendorId={vendor_id}")
    
    if result.get("success") and result.get("data"):
        filaments = result["data"]
        if isinstance(filaments, list) and len(filaments) > 0:
            for f in filaments:
                if f.get("name") == name and f.get("vendorId") == vendor_id:
                    print(f"✅ 找到耗材: {f['name']} (ID: {f['id']})")
                    return f["id"]
    return None

def create_filament(name, vendor_id, material, color_hex, price):
    """创建耗材"""
    filament_data = {
        "name": name,
        "vendorId": vendor_id,
        "material": material,
        "price": price if price else 0,
        "density": 1.24,
        "diameter": 1.75,
        "weight": 1000,
        "spoolWeight": 0
    }
    
    if color_hex:
        filament_data["colorHex"] = color_hex
    
    print(f"📦 创建耗材: {name}...")
    result = api_request("POST", "/api/v1/filaments", filament_data)
    
    if result.get("success"):
        filament_id = result["data"]["id"]
        print(f"✅ 耗材创建成功: {name} (ID: {filament_id})")
        return filament_id
    else:
        raise Exception(f"创建耗材失败: {result.get('message')}")

def create_spool(filament_id, price, location, registered_date, weight=1000, buy_date=None, shop=None):
    """创建线轴"""
    date_str = buy_date if buy_date else (registered_date[:10] if len(registered_date) > 10 else "")
    
    spool_data = {
        "filamentId": filament_id,
        "price": price if price else 0,
        "location": location if location else "",
        "registered": registered_date,
        "initialWeight": weight,
        "usedWeight": 0,
        "archived": False,
        "customFields": {
            "buy_date": date_str,
            "shop": shop if shop else location
        }
    }
    
    print(f"📦 创建线轴 (位置: {location}, 购买日期: {date_str})...")
    print(f"   自定义字段: buy_date={date_str}, shop={shop if shop else location}")
    result = api_request("POST", "/api/v1/spools", spool_data)
    
    if result.get("success"):
        spool = result["data"]
        print(f"✅ 线轴创建成功! ID: {spool['id']}, 位置: {spool['location']}")
        return spool
    else:
        raise Exception(f"创建线轴失败: {result.get('message')}")

def add_filament_record(brand, name, material, color, price, location, weight=1000, purchase_date=None):
    """
    添加新耗材记录的主流程
    
    流程:
    1. 从名称中提取纯颜色名（去材料前缀）
    2. 解析材料类型（PETG Matte 等）
    3. 转换颜色 HEX
    4. 查找/创建供应商
    5. 查找/创建耗材（名称只用颜色）
    6. 创建线轴
    """
    colors_map = load_colors()
    
    # Step 0: 提取纯颜色名
    extracted_color = extract_color_name(name, colors_map)
    print(f"🎨 颜色名提取: '{name}' -> '{extracted_color}'")
    
    # 用户单独提供 color 时优先用用户提供的
    final_color = color if color else extracted_color
    
    # Step 1: 颜色转换
    color_hex, color_display = color_to_hex(final_color, colors_map)
    color_not_found = color_hex is None
    
    if color_hex:
        note = " (映射表未找到，使用近似值)" if color_not_found else ""
        print(f"🎨 颜色: {final_color} -> {color_hex}{note}")
    else:
        color_hex = "#808080"  # 灰色占位
        print(f"🎨 颜色: {final_color} -> {color_hex} (未找到映射，使用占位值)")
    
    # Step 2: 材料类型解析
    material_resolved = resolve_filament_type(name, material)
    
    # Step 3: 耗材名称 = 纯颜色名
    filament_name = extracted_color
    print(f"📝 耗材名称: {filament_name}")
    
    # 购买日期
    if not purchase_date:
        purchase_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    else:
        purchase_date = purchase_date + "T00:00:00"
    print(f"📅 购买日期: {purchase_date}")
    
    # Step 4: 供应商
    brand_resolved = resolve_brand(brand)
    print(f"\n{'='*50}")
    print(f"Step 1: 处理供应商 '{brand_resolved}'")
    print(f"{'='*50}")
    vendor_id = find_or_create_vendor(brand_resolved)
    
    # Step 5: 耗材
    print(f"\n{'='*50}")
    print(f"Step 2: 查找耗材 '{filament_name}'")
    print(f"{'='*50}")
    filament_id = find_filament(filament_name, vendor_id)
    filament_exists = filament_id is not None
    
    if not filament_exists:
        print(f"\n{'='*50}")
        print(f"Step 3: 创建新耗材 '{filament_name}' (material: {material_resolved})")
        print(f"{'='*50}")
        filament_id = create_filament(filament_name, vendor_id, material_resolved, color_hex, price)
    else:
        print(f"\n⚠️ 耗材已存在，跳过创建步骤")
    
    date_str = purchase_date[:10] if len(purchase_date) > 10 else purchase_date
    
    # Step 6: 线轴
    print(f"\n{'='*50}")
    print(f"Step 4: 创建线轴")
    print(f"{'='*50}")
    spool = create_spool(filament_id, price, location, purchase_date, weight, buy_date=date_str, shop=location)
    
    # 汇总
    warn = f"\n⚠️ 颜色 '{final_color}' 未在映射表中找到，HEX 值 (#808080) 为占位值，请到 Spoolman 中手动修正" if color_not_found else ""
    
    print(f"\n{'='*50}")
    print(f"✅ 完成! 耗材记录已添加")
    print(f"{'='*50}")
    print(f"""
📋 记录汇总:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏭 供应商: {brand} (ID: {vendor_id})
🧵 耗材: {filament_name} (ID: {filament_id})
   材料类型: {material_resolved}
🎨 颜色: {final_color} ({color_hex}){(" (需修正)" if color_not_found else "")}
📦 线轴ID: {spool['id']}
📍 位置: {location}
💰 价格: {price}元
⚖️ 初始重量: {weight}g
📅 购买日期: {date_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {warn}
    """)
    
    return {
        "vendor_id": vendor_id,
        "filament_id": filament_id,
        "spool_id": spool["id"],
        "filament_exists": filament_exists,
        "color_not_found": color_not_found
    }

# ============ CLI 入口 ============
def main():
    parser = argparse.ArgumentParser(description="添加新耗材/线轴到 Spoolman")
    parser.add_argument("--brand", required=True, help="品牌/供应商名称")
    parser.add_argument("--name", required=True, help="耗材名称（颜色+表面处理，如 哑光苏军绿、红色银河宝石蓝）")
    parser.add_argument("--material", required=True, help="材料类型 (PLA, PETG, ABS, TPU 等)")
    parser.add_argument("--color", help="颜色名称（可选，会从 name 中提取）")
    parser.add_argument("--price", type=float, required=True, help="购买价格")
    parser.add_argument("--location", required=True, help="存放/购买位置")
    parser.add_argument("--weight", type=float, default=1000, help="线轴初始重量 (默认 1000g)")
    parser.add_argument("--date", help="购买日期 (格式: YYYY-MM-DD，默认今天)")
    
    args = parser.parse_args()
    
    try:
        result = add_filament_record(
            brand=args.brand,
            name=args.name,
            material=args.material,
            color=args.color,
            price=args.price,
            location=args.location,
            weight=args.weight,
            purchase_date=args.date,
        )
        print(f"\n[OUTPUT] {json.dumps(result, ensure_ascii=False)}")
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
