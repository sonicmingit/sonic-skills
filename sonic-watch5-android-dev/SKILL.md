---
name: sonic-小米手表开发
description: "开发、修复或移植国行 Xiaomi Watch 5 的 Android APK，复用已验证的原生工程、圆屏布局、资源加载和 BLE 排错经验。用于新建手表应用、真机问题诊断及开发交接；不用于 REDMI Watch 5、海外 Wear OS 或 Vela 应用。"
---

# sonic-小米手表开发

把新需求推进到可构建、可安装、验证边界明确的 APK；优先复用本机证据，减少重新搜参数、找工具和试错。适用基线来自 2026-11-04/05 的国行 eSIM 实机，不把历史事实当作当前设备在线状态。

## 使用方法

在新聊天中调用 `$sonic-小米手表开发`，并说明应用需求和目标工作目录。例如：“使用 $sonic-小米手表开发，在 E:\Code\Sonic\watch5 开发一个倒计时应用，支持开始、暂停和重置。”技能提供已验证的设备基线、工程入口和排错流程。

若技能列表尚未刷新，直接读取本 `SKILL.md`。本技能不包含 Android SDK、JDK、业务源码或个人签名；资料不可达时按下面说明处理，不冒充已经完成工程检查。

## 接手与最少读取

资料根目录默认 `E:/Code/Sonic/watch5`。用户指定了其他工作目录时，在用户目录做开发，资料根只供参考，不擅自把项目移回默认目录。资料已迁移则使用实际根目录。

1. 服从目标目录的 `AGENTS.md`；在本工作区先读 `Agent.md` 的当前摘要和 `WATCH5_DEVELOPMENT.md`，再读目标应用最新 README/暂停记录。历史日志仅在追溯相关问题时展开。
2. 根据下表读取 `WATCH5_ENGINEERING_GUIDE.md` 的相关章节，不每轮加载所有项目历史。`WATCH5_AGENT_QUICKSTART.md` 是人工交接入口，已读本技能且了解流程时按需查阅；目录规则要求必读时遵守目录规则。
3. 首次开发、迁移机器或工具报错时运行本技能的 `scripts/preflight.ps1`；普通文档/布局小改无需重复检查整个环境。

```powershell
# $skillRoot 替换为实际加载的 SKILL.md 所在目录。
pwsh -NoProfile -File "$skillRoot/scripts/preflight.ps1" -Workspace 'E:/Code/Sonic/watch5' -Profile ui
# Profile 可选 ui / ble / port / docs，分别对应界面、蓝牙、移植、文档。
# 脚本仅检查本地文件，不调用 ADB、安装或联网。
```

结果只说明路径存在，不证明工具可执行、设备连接或 APK 能运行。缺少指定工具时先检查路径/脚本参数，只补缺项。缺少资料根时说明来源不可达，先利用下面的已知基线推进可做的工作；不能宣称已读取历史证据或执行构建。

## 选择复用入口

以下路径相对资料根；读取后在目标项目改造，不覆盖参考工程。当前版本、授权和暂停状态始终回到专项记录读取，不写死在技能中。

| 当前任务 | 读取与复用 |
| --- | --- |
| 新建原生 APK | 工程手册 §2–4；`tesla-watch/preview-apk/build.ps1`、`AndroidManifest.xml`、`src/`。复制前去掉 Tesla 文案、资产、包名和模拟业务，不把整套车控原型当通用模板 |
| 圆屏布局/手势 | 工程手册 §5；`tesla-watch/preview-apk/qa/home-0.10-review.md` 与原生 View 实现；HTML 预览不能代替手表截图 |
| 图片缺失/WebView失败 | 工程手册 §6；`tesla-watch/preview-apk/design/RESOURCES_0.7.md`。先分文件打开、解码、绘制，旧资产缺失的精确根因未证实 |
| BLE或外设通信 | 工程手册 §7；`tesla-watch/ble-app/README.md`、`test.ps1`、`tesla-watch/probe/TEST_GUIDE.md`。会话认证与实际控制是否实现以最新记录为准 |
| 第三方 APK 移植/手机联动 | 工程手册 §8；`watch/analysis/ninebot-rea/COMPATIBILITY_RESULT.md`、`watch/analysis/ninebot-phone/bridge-probe/SESSION_2026-11-05.md` 及后续记录。固定 APK 补丁不可跨版本照搬 |
| 汇总/交接 | 工程手册 §9、`docs/watch5/PROJECT_TEMPLATE.md`；更新 `Agent.md` 的当前摘要，不只追加旧状态之后的新日志 |

## 已知基线及关键约束

- M2505W1、Android14/API34、480×480px、320dpi，名义全屏为 **240dp**；ABI 为 `armeabi-v7a, armeabi`。新设备/固件再核对，不因芯片支持64位就只提供arm64库。
- 已验证 Java + Activity/View/Canvas 与 SDK 命令行构建。Kotlin/Compose/Gradle 可按用户需求采用，但需单独验收；不默认 GMS、Wear Data Layer、OMS 或 Vela 可用。
- 固定图片优先 `res/drawable-nodpi` + `R.drawable`，aapt2 先生成 R 再编译。`assets/` 合法；检查最终 APK 资源和已安装版本，避免反复换图片格式掩盖文件打开错误。WebView 初始化通用报错不证明 provider 缺失。
- Canvas 的480设计坐标需统一缩放及触摸逆变换。圆屏中部放宽、上下收窄；字号、返回、翻页触控范围、键盘和大字号分别检查。Canvas 不会自动补齐字体缩放和 TalkBack 语义。
- 已有构建工具在 `tesla-watch/probe/.tools/`；JDK 默认 `D:/Scoop/apps/OracleJDK17/current`，均可重定位。保留现有包名/签名/钥匙数据；新应用独立包名。复制前检查个人默认配置，不复制 `.private/`、已生成个人 APK 或账号数据。
- ADB 每条设备命令明确 `-s` 目标；不随意重启共享服务或清数据。真实设备地址每次确认，不能复用历史 IP。启动后查看当前版本截图，黑屏、表盘、logo和别的应用都不能作为验收。
- BLE 权限、扫描、连接、发现、订阅、认证、发送、结果分阶段，均有取消和超时；拒绝旧回调。写入/队列成功不等于外设执行成功，未认证回复不等于配对完成。
- 无设备时完成代码、协议测试、构建和资源检查，列出待实测项。安装、启动、通信、账号授权、真实业务分别给证据。个人 VIN/密钥/令牌不进入通用文档，截图保护不为验收而关闭。

## 测试文件与日志导出

- 每次运行前先指定输出目录。电脑以当前工作区为基准，仅把生成的测试文件放入 `download/test/`，测试日志及应用导出日志的本地副本放入 `download/logs/`。禁止将测试产物散落在工作区根目录、源码目录、桌面或其他目录。按用途归类：测试生成的 XML、截图、模拟输入 JSON 归 test；诊断 JSON、logcat、错误报告归 logs。测试源码和正式 APK 按工程结构管理。
- 手表侧对应系统共享下载目录的 `Download/test/` 和 `Download/logs/`。所有应用内手动或自动导出（含诊断值、错误报告）统一写入后者，即使格式为 JSON、XML 或图片。Android 使用系统下载集合和相对路径 `Environment.DIRECTORY_DOWNLOADS + "/logs/"`，不硬编码挂载点。写入成功再提示实际文件名和位置；失败清理本次半成品并报告错误，不改投其他目录。
- 所有日志文件名以生成端本地时间 `yyyyMMdd-HHmmss` 开头，精确到秒，保留真实扩展名，如 `20261106-142443.json`。同秒重试或并发写入时独占创建并追加序号（如 `20261106-142443-02.json`），不得覆盖既有文件。日志正文按需记录应用、版本和带时区的时间，避免写入令牌、密钥等敏感数据。
- 交付前检查测试脚本、ADB 截图/拉取目标和应用导出路径，实际验证同秒连续导出可分别打开。只清理本次创建的临时文件。历史文件沿用原路径，迁移或删除须另有要求。

## 执行与收尾

新应用先跑通标题、图片、按钮、返回的最小原生页，再扩展业务。已有应用按请求做最小相关修改；不重新设计用户已确认的界面。新应用用项目模板记录要求，随后验证构建/签名/对齐/资源；需要上机时依现有授权安装核对。

缺少设备不必停止独立开发；但无账号/实体卡/现场条件时不能制造配对或控车成功。历史用户要求“两个 agent”、固定 MAC 或个人默认值不自动推广成新任务要求。汇总资料也不恢复其他暂停任务。

交付写明 APK 路径、版本、构建结果、实际验证和未覆盖范围；可复用的新结论写回工程手册，专项证据留在应用目录。

## 技能维护

唯一维护源位于当前 OneDrive 根目录下的 `AI/skills/sonic/sonic-watch5-android-dev/`。按 Sonic 规范从 `OneDrive`、`OneDriveConsumer`、`OneDriveCommercial` 环境变量定位；用户明确指定时使用指定位置，多候选或变量缺失按规范处理，不猜固定盘符。本机当前解析为 `E:/Sonic/OneDrive/AI/skills/sonic/sonic-watch5-android-dev/`，仅是本机记录。英文目录名与中文技能名不同，Codex 用户目录及原工作区使用链接指向维护源，避免独立副本分叉；保存在 OneDrive 目录不等于已经确认云端同步。

修改本技能前先读取同级 `sonic-skill-rules/SKILL.md`；每次实际变更更新 [CHANGELOG.md](CHANGELOG.md)，完成检查后按规范同步到 `sonicmingit/sonic-skills`。仅调用本技能开发手表应用不触发技能发布流程。通用校验器的小写英文命名约定不等于平台实际限制，不能仅据此把中文名称改回英文。
