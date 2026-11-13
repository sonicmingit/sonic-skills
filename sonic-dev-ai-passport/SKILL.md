---
name: sonic-dev-AIPassport开发规范
description: 按 Sonic 约定开发、移植、修复和交付 FoloToy AI Passport 应用，整合原 passport 技能流程、工作区归档、模型评估、中文 UI、通用 Web 配置页和固件验收。用于该硬件的应用开发及开发规范维护；不把设计原型或诊断请求当作烧录授权。
---

# sonic-dev-AIPassport开发规范

## 入口与范围

面向 FoloToy AI Passport（已记录基线 ESP32-C3、8MB Flash、无 PSRAM、ESP-IDF 5.5.3）。用户的任务和板型证据优先于本技能默认值。先定位当前工作区和目标源码，不假定另一台电脑有相同盘符。

读取工作区 `AGENTS.md`、`01-docs/README.md`，再读目标源码 `AGENTS.md`、`docs/README.md`、`docs/development/ai-guide.md`；先检查两个仓库各自的 `git status --short --branch`。本技能不能代替目标版本的 BSP、硬件资料与工程文档。

本技能整合原 `passport-develop` 的完整实施流程，并按阶段保留 `passport-setup`、`passport-build`、`passport-device-test`、`passport-debug`。不删除或覆盖这些上游技能。缺失时按目标源码 `skills/README.md` 安装并验证可读性；无法使用时读取对应工程文档，明确说明未调用该技能。

## 开发流程

1. 复用已有项目，保留 dirty 修改，不为获得干净环境自动 stash/reset/覆盖。已有应用继续对应分支；新应用基于已核实上游 main 提交建立独立源码和 `feature/<project-name>`。不把 demo 整枝或旧 BSP 配置合并为产品。关键板型/电气事实、产品行为或不可逆迁移不清楚时询问；普通选择自主完成并记录。
2. 先明确输入输出、页面、三键动作、状态转换、任务所有权、持久化、资源预算、异常恢复和验收。离线需求不额外引入 Wi-Fi、云服务、新接线或付费依赖。一般由 Sol 或 Astra 完成需求与设计，再读工作区模型文档评估实现阶段模型与推理档；不保证更省 token、不声称自动切换当前模型。
3. 按 [工作区规则](references/workspace-rules.md) 命名、建目录、记录模型评估、素材来源及截图。普通小改动简化文档，不为小改动建立庞大流程。
4. 按需求阅读 `docs/reference/README.md`、相关 demo、BSP 头文件和邻近实现。复用驱动与独立逻辑，重新设计应用页面、导航和三键交互；改标题/配色不算重设计。检查启动与返回路径不再进入原测试壳。
5. 应用状态/任务放 `main`，可复用板级能力放 `components/bsp`。引脚与地址以 `bsp_pins.h` 为准；外部任务访问 LVGL 必须持 `bsp_lvgl_lock()`，按键回调仅发轻量事件，销毁 UI 前停止所有访问它的任务/定时器/回调。复用 I2C/ADC 所有者，预算内部堆、连续块、DMA、栈、字体和无线/音频共存。
6. 中文不是仅改字符串：核对 UTF-8、静态/动态字符与标点字形、字号/样式和字体资产，检查真实渲染。默认 Montserrat 无中文字形；不隐藏缺字框。设备电量默认右上角读取 `bsp_battery_soc()`，-1 显示不可用，用户有其他布局要求时遵循其设计。
7. 涉及本地 Web 配置时，读取 [通用配置规范](references/web-config.md)，复用 `assets/passport-console-template.zip`。电脑第一版双栏、手机第二版向导、官网品牌、本地资源、稳定设备热点后缀和访问密码是公共约定；应用业务 UI 仍独立设计。模板目前为演示且存在 P2 密度待调，不能作为已接通后端的成品。
8. 小步运行相关检查，将状态机/协议/时间/布局逻辑与 ESP-IDF/LVGL 解耦并做有意义的主机测试。最终运行目标源码完整验证门禁，不隐藏失败，不拿旧构建产物当本轮结果。
9. 按 [构建与实机流程](references/validation.md) 交付校验过的 `0x0` 合并镜像、匹配 ELF/MAP/manifest 及 SHA-256。分别报告 Build、Host tests、Device tests、Unverified，更新项目 README、运行截图和总结。
10. 固件功能完成后主动询问是否刷机测试。具体端口、镜像和数据影响须获本次授权后才烧录；连接 USB 不等于授权，全片擦除单独确认，不强制原厂备份。纯文档/设计任务不刷无关固件。

## 按需路由

| 任务 | 使用技能/文档 |
| --- | --- |
| 工具链缺失或失活 | `passport-setup`；`docs/development/engineering/environment-setup.md` |
| 构建、依赖、分区和交付 | `passport-build`；`build-and-test.md`、`firmware-layout.md`（均在 engineering 下） |
| 获授权实机测试 | `passport-device-test`；AI guide 的 on-device handoff |
| 崩溃/黑屏/无声/缺字 | `passport-debug`；[诊断要点](references/validation.md)及硬件指南；只问诊断不实施修复 |
| 中文字体 | `docs/development/engineering/lvgl-chinese-fonts.md` |
| Wi-Fi/BLE 配网 | `docs/development/engineering/wifi-provisioning.md`；只复用实际支持的协议 |
| 公共配置页 | [规范](references/web-config.md)、模板 ZIP 中 README/SPEC；先阅读待验边界再接入 |

## 权限与交接

AI Passport 首次初始化时，设备 Wi-Fi 配置热点和本地 Web 配置页统一使用初始默认值 `12345678`。已有配置优先，保留设备上的实际密码。实际配置的凭据通过本机私有配置获取，禁止写入共享文档、模板或构建日志。不改变路由器、云账号、API 密钥或内部密钥。旧 NVS 只迁移相应配置，不清空其他数据；每次授权刷机后验证实际入口，协议格式不支持时说明。

应用代码不自动 commit/push/发布，也不上传固件、日志和密钥。上游维护文档默认英文及 `.zh_CN.md` 成对；工作区与本技能管理文档中文。普通功能不修改上游发布 CHANGELOG。本技能自身的维护按 Sonic 技能规则同步，与应用仓库提交授权分开。

阶段交接记录已确定需求、未决事项、源码位置/分支/dirty、准确构建身份、验证结果及下一步。不能把编译、模拟器截图或刷写成功写成真机验收。来源与覆盖范围见 [来源记录](references/provenance.md)。
