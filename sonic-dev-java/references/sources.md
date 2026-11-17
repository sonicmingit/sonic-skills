# 来源与待讨论项

核验日期为 2026-11-17。

- 阿里官方仓库仍标示黄山版，发布日期 2022-02-03。https://github.com/alibaba/p3c
- 官方手册下载入口 https://github.com/alibaba/p3c/blob/master/Java开发手册(黄山版).pdf
- Spring Boot 代码组织 https://docs.spring.io/spring-boot/reference/using/structuring-your-code.html
- Spring Cloud 版本兼容入口 https://spring.io/projects/spring-cloud
- Code Review 候选 https://github.com/axross/skills/blob/main/.agents/skills/code-review/SKILL.md

本版以官方手册链接作为规范入口，未打包 PDF。阿里注释固定比例尚未核实，暂按注释覆盖职责和复杂逻辑验收。
默认按领域分包是本技能的工程选择，Spring Boot 并未强制唯一分层。Spring Cloud 服务边界、复用策略及模型能力分级属于用户要求与本技能补充。

后续可一起确定默认 JDK/Boot 版本、Maven 或 Gradle、MyBatis 或 JPA、API 返回格式、测试覆盖率目标及质量门禁。初版从目标项目读取这些约定，避免跨项目强行统一。
