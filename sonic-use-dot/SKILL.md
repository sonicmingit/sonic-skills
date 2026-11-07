---
name: sonic-use-墨水屏控制
description: 通过 Dot API 控制 Quote/0 墨水屏设备，支持推送文本或图片、查询设备状态和内容列表；在用户请求操作 Dot 墨水屏时使用。
---

# sonic-use-墨水屏控制

通过 Dot. API 远程控制墨水屏设备（Quote/0），支持文本推送、图片推送（自动 Base64 转换）和状态查询。

> Skill 目录：`~/.openclaw/skills/sonic-use-dot/`
> 执行脚本：`dot.py`
> 配置：`~/openclaw/secrets.yaml` 中的 `devices.dot` 项

---

## 前置配置

在 `~/openclaw/secrets.yaml` 中添加：

```yaml
devices:
  dot:
    api_key: "dot_app_xxxxx"
    devices:
      - name: "home"
        device_id: "9C9E6E3B88B8"
      - name: "work"
        device_id: "48F6EE5476C4"
```

- **api_key**：Dot. App → 设置 → API Key
- **device_id**：Dot. App → 设备详情 → 序列号
- 支持多设备，通过 `name` 别名引用

---

## 命令一：发送文本

```
发送文本到 Dot
设备：work
标题：每日提醒
正文：喝水时间到了！\n今日已喝：3杯
署名：健康助手
图标：~/Pictures/water.png
链接：x-apple-health://
立即显示：是
```

**等价命令行：**
```bash
python3 dot.py text -t "每日提醒" -m "喝水时间到了！\n今日已喝：3杯" -s "健康助手" -i ~/Pictures/water.png -l "x-apple-health://"
```

**字段说明：**

| 字段 | 命令行参数 | 必填 | 说明 |
|------|-----------|------|------|
| 设备 | `-d <name>` | ✅ | secrets.yaml 中的设备别名 |
| 标题 | `-t <str>` | - | 屏幕上显示的标题 |
| 图标 | 自动注入 🦞 | - | 不指定 `-i` 时自动使用 🦞 龙虾图标（Base64 预置） |
| 正文 | `-m <str>` | - | 正文内容，支持 `\n` 换行 |
| 署名 | `-s <str>` | - | 右下角署名 |
| 链接 | `-l <url>` | - | NFC 点击跳转目标（http/https/URL Scheme） |
| 立即显示 | `--no-refresh` | - | 不指定则立即显示，指定则下次切换生效 |
| taskKey | `--task-key <key>` | - | 指定更新哪条 Text API 内容 |

**对应 API**：`POST /api/authV2/open/device/:deviceId/text`

---

## 命令二：发送图片

```
发送图片到 Dot
设备：work
图片路径：~/qrcode.png
链接：https://example.com
边框：白色
抖动类型：误差扩散
抖动算法：Floyd-Steinberg
立即显示：是
```

**等价命令行：**
```bash
python3 dot.py image ~/photo.jpg --photo           # 照片模式：Atkinson 抖动（适合照片/复杂图）
python3 dot.py image ~/qrcode.png --border white   # 文字模式：NONE 抖动（适合文字/高对比图）
```

**字段说明：**

| 字段 | 命令行参数 | 必填 | 说明 |
|------|-----------|------|------|
| 设备 | `-d <name>` | ✅ | secrets.yaml 中的设备别名 |
| 图片路径 | `<path>` | ✅ | 本地图片，支持 PNG/JPG 等，自动转为 296×152px PNG 并 Base64 |
| 链接 | `-l <url>` | - | NFC 点击跳转目标 |
| 边框 | `--border white/black` | - | 白色=0（默认），黑色=1 |
| 照片模式 | `--photo` | - | 使用 Atkinson 抖动（适合照片）；默认 NONE 抖动（适合文字/高对比图） |
| 抖动类型 | `-d2 diffusion/ordered/none` | - | 覆盖默认参数 |
| 抖动算法 | `-k <algorithm>` | - | 覆盖默认参数 |
| 立即显示 | `--no-refresh` | - | 不指定则立即显示 |
| taskKey | `--task-key <key>` | - | 指定更新哪条 Image API 内容 |

**抖动算法（ditherKernel）选项：**

| 算法 | 适用场景 |
|------|---------|
| `FLOYD_STEINBERG` | 误差扩散（默认），效果自然 |
| `ATKINSON` | 高对比度线条图；推荐与 `--photo` 配合使用 |
| `THRESHOLD` | 简单二值图 |
| `NONE` | **默认**；关闭抖动，纯文字/高对比图最锐利 |

**对应 API**：`POST /api/authV2/open/device/:deviceId/image`

---

## 命令三：查询设备状态

```
查询 Dot 状态
设备：home
```

```
查询 Dot 状态
```

**等价命令行：**
```bash
python3 dot.py status work
python3 dot.py status              # 不填设备，查所有已配置设备
```

返回：系统版本、当前状态（活跃/休眠）、电池、WiFi 信号、下次渲染时间。

**对应 API**：`GET /api/authV2/open/device/:deviceId/status`

---

## 命令四：查询设备内容列表

```
查询 Dot 内容
设备：work
内容类型：loop
```

**等价命令行：**
```bash
python3 dot.py list loop work
python3 dot.py list               # 默认查 loop
python3 dot.py list fixed        # 查固定内容
```

返回设备上所有内容项，每项包含 `type`、`key`（即 taskKey）、`refreshNow` 等字段。

**对应 API**：`GET /api/authV2/open/device/:deviceId/:taskType/list`

---

## 通用说明

**限速**：10 requests / second，所有接口共享配额。

**设备离线行为**：设备休眠时数据正常更新，下次切换时自动呈现，不算错误。

**taskKey**：一台设备可有多条 Text/Image API 内容，通过 List 命令获取 `key` 字段，传入 `--task-key` 指定操作哪条。

**权限错误（403）**：检查 API Key 是否有权操作该设备。

---

## 依赖

```bash
pip install pyyaml Pillow
```

---

## 实测最优参数（鸣的 work 设备）

以下参数已固化为脚本默认值：

| 类型 | 参数 | 说明 |
|------|------|------|
| **文字转图片** | `ditherType=NONE`, `border=0` | 默认，文字最锐利 |
| **照片** | `--photo`（Atkinson） | 复杂照片推荐 |
| **纯文本（Text API）** | 自动加 🦞 图标 | 无需手动指定 |

对比结论：

| 配置 | ditherType | border | 效果 |
|------|-----------|--------|------|
| 无抖动+白 | **NONE** | **0** | **最佳**（文字/高对比图） |
| Atkinson | DIFFUSION/ATKINSON | 0 | 较好（照片） |
| Threshold | DIFFUSION/THRESHOLD | 0 | 一般 |
