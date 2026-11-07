---
name: sonic-svc-3D打印机状态
description: |
  汇报/查看/发送 3D 打印机（Bambu Lab H2C 和 A1Mini）状态。

  【触发词】
  「汇报一下打印机状态」
  「查看打印机状态」
  「发送打印机状态」
  「打印机状态」
  「打印状态」
  「3D打印机状态」
  「H2C状态」
  「A1MINI状态」
  「拓竹状态」

  【功能】
  1. 通过 Home Assistant API 查询 H2C 和 A1Mini 的打印状态
  2. 若正在打印，获取摄像头截图并用 AI 分析是否有异常
  3. 汇总所有信息，通过飞书 message 工具发送图片（唯一可用方式）
---

# sonic-svc-3D打印机状态

## HA API 配置（已存储在 secrets.yaml）

- HA 地址：`http://10.0.0.88:8124`
- Token：从 `~/openclaw/secrets.yaml` 读取 `homeassistant.token`

## H2C 实体 ID

| 实体 | 用途 |
|---|---|
| `sensor.h2c_31b8dp5c0700638_print_progress` | 打印进度 % |
| `sensor.h2c_31b8dp5c0700638_remaining_time` | 剩余时间 min |
| `sensor.h2c_31b8dp5c0700638_current_layer` | 当前层数 |
| `sensor.h2c_31b8dp5c0700638_nozzle_temperature` | 喷嘴温度 |
| `sensor.h2c_31b8dp5c0700638_bed_temperature` | 热床温度 |
| `camera.h2c_31b8dp5c0700638_camera` | 摄像头 |

## A1Mini 实体 ID

| 实体 | 用途 |
|---|---|
| `sensor.bambu_a1mini_print_progress` | 打印进度 % |
| `sensor.bambu_a1mini_current_stage` | 当前阶段（idle/running/...) |
| `binary_sensor.bambu_a1mini_online` | 在线状态 |
| `sensor.bambu_a1mini_nozzle_temperature` | 喷嘴温度 |
| `sensor.bambu_a1mini_bed_temperature` | 热床温度 |
| `camera.bambu_a1mini_camera` | 摄像头 |

## 执行流程

1. **读取 Token**：`TOKEN=$(grep -A2 "homeassistant:" ~/openclaw/secrets.yaml | grep token | awk -F'"' '{print $2}')`
2. **查询两台打印机状态**：运行 `scripts/report.sh`，获取 JSON 输出
3. **判断是否在打印**：进度>0 且 阶段非 idle
4. **在打印时**：图片已下载到 workspace，从 JSON 的 `image` 字段取路径
5. **AI 分析**：用 image 工具分析截图
6. **发送结果**：用 `message(action=send, media=图片路径, caption="...")` 发送图片+文字汇总
7. **清理**：从 JSON 的 `_cleanup` 字段获取需删除的文件路径，发送成功后删除

```bash
# 清理命令示例
rm -f /home/sonic/openclaw-workspaces/hass/printer_h2c.jpg
```

## 重要：图片发送方式

**必须用 `message` 工具发送图片**，不要用 `MEDIA:` 指令（会退化成文本链接）。

正确方式：
```json
{
  "action": "send",
  "channel": "feishu",
  "media": "/home/sonic/openclaw-workspaces/hass/printer_h2c.jpg",
  "caption": "H2C 当前打印画面"
}
```

图片保存目录：`/home/sonic/openclaw-workspaces/hass/`（此目录在 image 工具和白板中均可用）

⚠️ 注意：image 工具只支持 workspace 目录，不支持技能自己的 sandbox 目录。每次调用完成后必须清理临时图片。

## 状态汇总模板

```
### 🖨️ Bambu Lab H2C 打印状态
| 项目 | 数值 |
|---|---|
| 📶 在线状态 | **在线/离线** |
| 📊 当前阶段 | **待机/打印中** |
| 🔰 打印进度 | **XX%** |
| ⏳ 剩余时间 | **XX min** |
| 📊 当前层数 | 第 **XX** 层 |
| 🌡️ 喷嘴温度 | **XX°C** |
| 🛏️ 热床温度 | **XX°C** |

### 🖨️ Bambu Lab A1Mini 状态
| 项目 | 数值 |
|---|---|
| 📶 在线状态 | **在线/离线** |
| 📊 当前阶段 | **待机/打印中** |
| 🔰 打印进度 | **XX%** |
| ⏳ 剩余时间 | **XX min** |
| 📊 当前层数 | 第 **XX** 层 |
| 🌡️ 喷嘴温度 | **XX°C** |
| 🛏️ 热床温度 | **XX°C** |
```
