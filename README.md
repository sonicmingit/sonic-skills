# Sonic 自定义技能

目录统一使用 `sonic-类别-英文用途`，名称使用 `sonic-类别-中文用途`。分类目录保持扁平。

本清单于 2026-11-07 按现有技能维护源整理。

| 类别 | 中文名称 | 当前目录 | 原目录 |
|---|---|---|---|
| dev | [sonic-dev-SD2开发指南](sonic-dev-sd2/SKILL.md) | `sonic-dev-sd2` | `sonic-sd2-development` |
| dev | [sonic-dev-小米手表开发](sonic-dev-watch5/SKILL.md) | `sonic-dev-watch5` | `sonic-watch5-android-dev` |
| ops | [sonic-ops-飞书插件运维](sonic-ops-openclaw-lark/SKILL.md) | `sonic-ops-openclaw-lark` | `sonic-openclaw-lark-manual-update` |
| rules | [sonic-rules-技能创建规范](sonic-rules-skills/SKILL.md) | `sonic-rules-skills` | `sonic-rules-skills` |
| svc | [sonic-svc-3D打印机状态](sonic-svc-printer-status/SKILL.md) | `sonic-svc-printer-status` | `sonic-3d-printer-status` |
| svc | [sonic-svc-耗材管理](sonic-svc-spoolman/SKILL.md) | `sonic-svc-spoolman` | `sonic-spoolman-filament-record` |
| use | [sonic-use-墨水屏控制](sonic-use-dot/SKILL.md) | `sonic-use-dot` | `sonic-dot` |
| use | [sonic-use-Gemini图片生成](sonic-use-gemini-image/SKILL.md) | `sonic-use-gemini-image` | `sonic-gemini-oai-image` |
| use | [sonic-use-横纵分析与得到笔记](sonic-use-khazix-analysis-getnote/SKILL.md) | `sonic-use-khazix-analysis-getnote` | `sonic-khazix-analysis-getnote` |
| use | [sonic-use-写作与飞书笔记](sonic-use-khazix-feishu-note/SKILL.md) | `sonic-use-khazix-feishu-note` | `sonic-khazix-feishu-note` |
| use | [sonic-use-局域网打印](sonic-use-lan-printing/SKILL.md) | `sonic-use-lan-printing` | `sonic-lan-printing` |
| use | [sonic-use-MiniMax图片生成](sonic-use-minimax-image/SKILL.md) | `sonic-use-minimax-image` | `sonic-minimax-image` |
| use | [sonic-use-小米MiMo语音](sonic-use-xiaomi-mimo-tts/SKILL.md) | `sonic-use-xiaomi-mimo-tts` | `sonic-xiaomi-mimo-tts` |

`rules` 为规范流程；`dev` 为开发；`use` 为通用工具、平台及设备操作；`svc` 为自部署服务的业务操作；`ops` 为部署升级等运行维护。

OneDrive 维护源从环境变量定位到 `AI/skills/sonic`。Codex 当前安装总规则、SD2 开发和小米手表开发三个技能，安装目录使用指向维护源的链接；其余技能的脚本及运行依赖按各自说明准备。

上传与下载的流程见 [技能创建规范](sonic-rules-skills/SKILL.md)。安装旧版本的机器可根据上表原目录识别改名，并调整已有安装入口。不要把旧目录缺失视为卸载，也不要保留新旧重复安装。
