# 本地资料与来源

## 阿里手册
- 名称：《Java 开发手册》黄山版，2022-02-03 发布；2026-11-17 下载时官方 README 仍列为最新版。
- 原始地址：https://github.com/alibaba/p3c/blob/master/Java开发手册(黄山版).pdf
- 本地原版：[manual.pdf](alibaba/manual.pdf)，55 个 PDF 页面（含封面目录等），未修改。
- 本地全文：[manual.txt](alibaba/manual.txt)，由原版提取并增加 PDF 页码分隔，可能有断行或字符提取误差。
- PDF SHA-256：`68463b8cc5f1ad8f9c4fcaaa7c468a46a7e603b23cd22f38414697782b404f1f`。
- [上游说明快照](alibaba/upstream-readme.md) （仅将相对仓库链接改为绝对链接）标示 Apache-2.0；随附 [许可证](alibaba/LICENSE-2.0.txt)。版权归原作者；本技能正文是归纳及项目补充，非官方修订版。

使用时不访问以上网址，只在本地全文搜索章节与关键词，再按页码查看 PDF。正文重点规则优先执行，其余按当前任务阅读对应章节：命名风格、OOP 规约、集合处理、并发处理、注释规约、异常处理、日志规约、单元测试、安全规约、SQL 语句、ORM 映射、工程结构、设计规约。不要每次把整本手册载入上下文。

注释规约位于 PDF 第 23—24 页（正文 20—21 页），未设置注释百分比。中文注释、复用要求和确认后审查是本技能额外强制要求；作者信息必须真实，不以 Agent 名称补齐作者字段。

## 框架与选型
Spring Boot 不强制唯一包布局；按业务分包和分层是本技能默认组织建议，已有合理项目布局优先。官方依据：https://docs.spring.io/spring-boot/reference/using/structuring-your-code.html 。Spring Cloud 兼容资料：https://spring.io/projects/spring-cloud 。这些仅为溯源链接，阿里规范执行不依赖联网。项目框架 API/兼容性核验不应被误解为联网查阿里规范。
JDK、构建工具、ORM、数据库及版本均由项目决定，不设固定组合。

## Code Review 方法来源
- 候选：https://github.com/axross/skills/tree/main/.agents/skills/code-review
- 检查的提交：`cce7ecf35435cc666813cb26ad75c30a261cdcc5`，日期 2026-11-17。
- 未在该仓库检索到 LICENSE 文件，故不复制分发上游全文。内置 review.md 是参考其一般审查方法自行编写的中文 Java 流程，可直接本地执行，无外部技能依赖。
