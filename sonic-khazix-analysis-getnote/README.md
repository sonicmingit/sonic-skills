# sonic-khazix-analysis-getnote Skill

横纵分析法：AI时代快速建立认知框架的通用研究方法论。[Created by Sonic]

## 功能特性

- 生成 1-3 万字深度研究报告
- 纵向分析：历史发展脉络、关键节点、决策逻辑
- 横向分析：竞品对比、市场定位、生态位分析
- 自动保存到本地文件（.md 和 .pdf）
- 自动同步到 Get笔记知识库

## 使用方法

直接告诉 Claude：

```
用卡兹克纵横分析法研究 Harness Engineering
用横纵分析法分析 Claude Code
帮我研究一下 MCP 协议的前世今生
```

## 适用范围

- **产品/工具**：如 Hermes Agent、Cursor、Claude Code
- **公司/组织**：如 Anthropic、字节跳动、OpenAI
- **技术概念**：如 MCP协议、RAG、Agent框架
- **人物**：如某个行业关键人物的职业轨迹

## 配置要求

### 1. 环境变量

设置 Get笔记 API 凭证：

```bash
export GETNOTE_API_KEY="gk_live_你的key"
export GETNOTE_CLIENT_ID="cli_你的id"
```

### 2. Python 脚本

本Skill自带两个Python脚本：

- `scripts/md_to_pdf.py` - 将Markdown转换为PDF
- `scripts/save_to_getnote.py` - 将报告保存到Get笔记

**依赖安装**：
```bash
pip install weasyprint markdown --break-system-packages
```

## 知识库

默认保存到知识库：`eYxz6N4J`（卡兹克纵横分析法）

## 输出格式

1. **本地文件**
   - `{研究对象}.md` - Markdown 格式报告
   - `{研究对象}.pdf` - PDF 格式报告

2. **Get笔记**
   - 笔记标题：【横纵分析】研究对象
   - 标签：卡兹克纵横分析法、Deep Research、自动生成
   - 知识库：卡兹克纵横分析法

## 脚本使用

### 保存到Get笔记

```bash
python scripts/save_to_getnote.py "【横纵分析】研究对象" ./研究对象.md [知识库ID]
```

**参数说明**：
- 第一个参数：笔记标题
- 第二个参数：Markdown文件路径
- 第三个参数（可选）：知识库ID，默认为 `eYxz6N4J`

### 生成PDF

```bash
python scripts/md_to_pdf.py input.md output.pdf --title "研究对象名称" --author "数字生命卡兹克"
```

## 方法论来源

- 开源仓库：https://github.com/KKKKhazix/khazix-skills
- 作者：数字生命卡兹克
