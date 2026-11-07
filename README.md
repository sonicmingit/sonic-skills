# Sonic 自定义技能库

这里集中维护 Sonic 创建或定制的 Agent 技能，涵盖开发、工具使用、自部署服务操作及运行维护。每个技能独立存放，具体使用条件和步骤见对应的 `SKILL.md`。

最后更新：**2026-11-07**。当前共 **14 个技能**。

## 分类与命名

| 类别 | 数量 | 适用范围 |
|---|---:|---|
| `rules` | 1 | 规范、约定、创建与维护流程 |
| `dev` | 2 | 应用或固件开发、移植与调试 |
| `use` | 7 | 通用工具、外部平台和设备操作 |
| `svc` | 2 | 自部署服务的业务操作 |
| `ops` | 2 | 服务部署、升级、备份、恢复与排错 |

- 英文目录：`sonic-类别-英文用途`，例如 `sonic-dev-watch5`。
- 中文名称：`sonic-类别-中文用途`，例如 `sonic-dev-小米手表开发`。
- 仓库保持扁平目录，不额外嵌套分类文件夹。
- 同一服务的业务操作归 `svc`，部署和运行维护归 `ops`。运行机器及环境要求写入技能说明。

## 技能说明与导航

### rules：规范与流程

| 技能名称 | 目录与文档 | 用途 |
|---|---|---|
| sonic-rules-技能创建规范 | [sonic-rules-skills](sonic-rules-skills/SKILL.md) | 统一技能分类、命名、中文文档、更新日志和仓库索引，管理 OneDrive、GitHub 与本机技能之间的同步。 |

### dev：开发

| 技能名称 | 目录与文档 | 用途 |
|---|---|---|
| sonic-dev-SD2开发指南 | [sonic-dev-sd2](sonic-dev-sd2/SKILL.md) | 为 ESP8266 SD2 桌面小电视开发或移植固件，查询硬件引脚，诊断刷写、启动与显示问题。 |
| sonic-dev-小米手表开发 | [sonic-dev-watch5](sonic-dev-watch5/SKILL.md) | 国行 Watch 5 APK 开发；先设计再按难度选择子 Agent 模型，复用圆屏/BLE 经验及固定签名备份，支持换机恢复。 |

### use：工具、平台与设备使用

| 技能名称 | 目录与文档 | 用途 |
|---|---|---|
| sonic-use-墨水屏控制 | [sonic-use-dot](sonic-use-dot/SKILL.md) | 通过 Dot API 向 Quote/0 墨水屏推送文字或图片，并查询设备状态及内容。 |
| sonic-use-Gemini图片生成 | [sonic-use-gemini-image](sonic-use-gemini-image/SKILL.md) | 通过兼容 OpenAI 的 API 调用 Gemini 图片模型，支持自定义接口地址。 |
| sonic-use-横纵分析与得到笔记 | [sonic-use-khazix-analysis-getnote](sonic-use-khazix-analysis-getnote/SKILL.md) | 对产品、公司或技术开展横纵分析，生成 PDF 研究报告，并保存到得到笔记。 |
| sonic-use-写作与飞书笔记 | [sonic-use-khazix-feishu-note](sonic-use-khazix-feishu-note/SKILL.md) | 根据主题调用写作规范产出文章，并保存到指定飞书知识库目录。 |
| sonic-use-局域网打印 | [sonic-use-lan-printing](sonic-use-lan-printing/SKILL.md) | 使用 CUPS 打印文件、管理打印队列及排错，支持试卷答案尾页识别与预处理。 |
| sonic-use-MiniMax图片生成 | [sonic-use-minimax-image](sonic-use-minimax-image/SKILL.md) | 使用 MiniMax 接口完成文生图和图生图。 |
| sonic-use-小米MiMo语音 | [sonic-use-xiaomi-mimo-tts](sonic-use-xiaomi-mimo-tts/SKILL.md) | 将文本或朗读稿转换为语音，支持带风格的朗读稿和语音回复流程。 |

### svc：自部署服务的业务操作

| 技能名称 | 目录与文档 | 用途 |
|---|---|---|
| sonic-svc-3D打印机状态 | [sonic-svc-printer-status](sonic-svc-printer-status/SKILL.md) | 通过 Home Assistant 查询拓竹 H2C 和 A1Mini 状态，结合摄像头截图分析并发送报告。 |
| sonic-svc-耗材管理 | [sonic-svc-spoolman](sonic-svc-spoolman/SKILL.md) | 在 Spoolman 中查询或创建品牌、耗材和线轴，记录新购耗材的价格、重量与存放位置。 |

### ops：运行维护

| 技能名称 | 目录与文档 | 用途 |
|---|---|---|
| sonic-ops-规范部署 | [sonic-ops-deploy](sonic-ops-deploy/SKILL.md) | 生成或执行 Docker 部署，整理已有目录，保留实例配置与数据，处理代码更新、配置合并和失败恢复。 |
| sonic-ops-飞书插件运维 | [sonic-ops-openclaw-lark](sonic-ops-openclaw-lark/SKILL.md) | 在官方自动升级失败时，备份并手动更新 OpenClaw 飞书插件，检查配置和升级结果。 |

## 使用与同步

1. 从上方选择技能，阅读其 `SKILL.md`，按说明准备运行环境、连接和依赖。不同技能可能依赖 Codex、OpenClaw、外部平台或特定设备。
2. 将所需技能安装或链接到当前 Agent 可读取的技能目录；优先链接维护源，避免独立副本分叉。在 Codex 中，用户级技能目录为已设置的 `$CODEX_HOME/skills`，未设置时使用 `~/.codex/skills`。
3. 在对话中使用技能的中文名称并说明任务，例如“使用 sonic-dev-小米手表开发，帮我开发一个倒计时应用”。

维护源默认从 `OneDrive`、`OneDriveConsumer` 或 `OneDriveCommercial` 环境变量定位到 `AI/skills/sonic`，不固定盘符。同步方式由 [技能创建规范](sonic-rules-skills/SKILL.md) 定义：

- **“推送一下我的更新”**：当前技能更新 → OneDrive 对应目录 → GitHub。
- **“检测我创建的技能”**：检查本机自建技能，汇总可确认的更新并按规则推送。
- **“查看技能有没有更新”**：查询 GitHub → 下载到 OneDrive → 更新当前 Agent 的安装入口或副本。
- **“只查看，不更新”**：只报告差异。

每个技能的内容变更记录在其目录的 `CHANGELOG.md`。同步时先检查差异，保护本地未同步修改；单纯下载安装既有版本不额外制造更新日志。具体参数、权限和凭据读取方式以技能文档为准，凭据不存放在本说明中。

## 旧目录迁移对照

以下映射记录 2026-11-07 的分类迁移，供已安装旧版本的机器识别改名。总规则技能当前目录保持 `sonic-rules-skills`。

| 原目录 | 当前目录 |
|---|---|
| `sonic-3d-printer-status` | `sonic-svc-printer-status` |
| `sonic-dot` | `sonic-use-dot` |
| `sonic-gemini-oai-image` | `sonic-use-gemini-image` |
| `sonic-khazix-analysis-getnote` | `sonic-use-khazix-analysis-getnote` |
| `sonic-khazix-feishu-note` | `sonic-use-khazix-feishu-note` |
| `sonic-lan-printing` | `sonic-use-lan-printing` |
| `sonic-minimax-image` | `sonic-use-minimax-image` |
| `sonic-openclaw-lark-manual-update` | `sonic-ops-openclaw-lark` |
| `sonic-sd2-development` | `sonic-dev-sd2` |
| `sonic-spoolman-filament-record` | `sonic-svc-spoolman` |
| `sonic-watch5-android-dev` | `sonic-dev-watch5` |
| `sonic-xiaomi-mimo-tts` | `sonic-use-xiaomi-mimo-tts` |

迁移时调整现有安装链接和引用，保留技能历史，避免新旧目录重复安装。

## 本说明的维护规则

新增技能时，在同一次提交中更新本 README 的分类、中文名称、英文目录、用途、技能链接、总数及分类数量。改名、分类调整、用途变化、删除或归档时，也更新相关条目并保留历史迁移映射。发布前核对清单与实际技能目录一致，链接可访问；有实际内容更新时再更新维护日期。
