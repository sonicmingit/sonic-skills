# 来源与维护

首次整合：2026-11-07。上游仓库 https://github.com/FoloToy/ai-passport ，工作区已核实基线 `488beda41309f052d81f08d0016d65a3fd85eb7e`。

已读取本机原 `passport-develop`、`passport-setup`、`passport-build`、`passport-device-test`、`passport-debug` 的 SKILL.md；其范围与关键约束已合入本技能正文及 validation.md。继续保留原技能供具体阶段使用，不替换上游工程文档或声明与未来版本自动同步。上游 MIT 许可保留于 `LICENSE.upstream.txt`。

| 原内容 | 新技能承载 |
| --- | --- |
| develop：需求/分支/重设计/BSP/验证/交接 | SKILL.md 开发流程 |
| setup：版本激活、最小修复、平台/USB边界 | validation.md 环境 |
| build：完整门禁、准确配置、归档和 0x0 | validation.md 构建归档 |
| device-test：具体授权、数据影响、有限观察 | validation.md 实机授权与测试 |
| debug：匹配 ELF、证据分层、诊断/修复边界 | validation.md 运行时故障诊断 |
| Sonic：目录、命名、模型、截图、总结 | workspace-rules.md |
| Sonic：固定密码、BSP、中文和权限规则 | SKILL.md 及 validation.md |
| 通用配置页：用户选择与接口约束 | web-config.md、assets/passport-console-template.zip |

公共模板由本工作区 passport-console 原型筛选，仅带必要前端文件、依赖锁、品牌图标与来源说明。没有真实设备 API、凭据、构建缓存、用户日志或效果图。模板仍有已记录视觉待验，不提升成固件验证结论。

维护本技能先读取 sonic-rules-技能创建规范；默认维护源从 OneDrive 环境变量解析 `AI/skills/sonic/sonic-dev-ai-passport`，当前 Agent 安装入口优先链接维护源。工作区 `06-templates/skills/` 只是交付快照；修改后同步快照/模板版本，避免两份独立编辑。正文、引用、素材实际变化均记录中文 CHANGELOG，更新仓库 README 后按 Sonic 规则同步。
