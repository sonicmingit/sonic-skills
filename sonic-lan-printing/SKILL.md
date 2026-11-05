---
name: sonic-lan-printing
description: LAN printer operations via CUPS (lp/lpstat/cancel), including setup verification, test prints, and common troubleshooting. Use when the user says print/打印, wants to print a PDF/image/text file, asks how to add/use the Brother DCP-T725DW (Brother_T725DW queue), or needs to diagnose stuck print jobs/queues.
---

# LAN Printing (CUPS)

提供一套可复用的“局域网打印”工作流：检查 CUPS/队列 → 测试打印 → 打印文件 → 排障。

## Quick start（最常用）

### 试卷 PDF：自动跳过“答案页”（尾页）
当用户发来 PDF 并且文本中命中“试卷/考试/模拟/复习/语文/数学/英语…”等关键词时，本技能会在打印前自动扫描**最后 3 页**，如果发现“答案/参考答案/解析/Answer Key”等关键词，则只打印答案页之前的页面。

可调参数（环境变量）：
- `EXAM_MODE=off`：关闭该行为（总是打印全部页）
- `TAIL_SCAN_PAGES=3`：扫描尾页数量（最小尾窗）
- `TAIL_SCAN_FRACTION=0.25`：按文档比例扫描尾部（如 40 页扫描后 10 页；与 TAIL_SCAN_PAGES 取更大值）
- `TAIL_SCAN_MAX_PAGES=20`：尾部扫描最大页数（防止 OCR 太慢）
- `EXAM_KEYWORDS_REGEX=...`：判定“试卷”的关键词正则
- `ANSWER_KEYWORDS_REGEX=...`：判定“答案页”的关键词正则
- `PRINT_ALL=1`：强制不裁剪（覆盖一切自动判断）

### 1) 检查 CUPS 是否在跑
```bash
lpstat -r
```
期望输出包含：`scheduler is running`（或中文“调度器正在运行”）。

### 2) 查看可用打印机队列
```bash
lpstat -p -d
```

### 3) 打一张最小测试页（纯文本）
```bash
echo "OpenClaw test page $(date)" | lp -d Brother_T725DW -t "OpenClaw test page"
```

### 4) 打印一个文件（PDF/图片/文本）
```bash
lp -d Brother_T725DW /path/to/file.pdf
```

## Workflow: 打印任务处理流程

### Step 0 — 安全与敏感信息
- 管理页密码等敏感信息只允许存放在 `~/openclaw/secrets.yaml`。
- 技能/知识库里只记录：IP/队列名/协议/常见命令，不记录明文密码。

### Step 1 — 发现与确认打印机（推荐方式：IPP/AirPrint）
在当前环境（Brother DCP‑T725DW）上，已通过 mDNS/IPP 发现过：
- IPP endpoint（示例）：`ipp://Brother.local:631/ipp/print`

如果需要重新发现：
```bash
which ippfind && ippfind | head
```

### Step 2 — 设定默认打印机（可选）
```bash
sudo lpadmin -d Brother_T725DW
lpstat -d
```

### Step 3 — 打印与队列观察
- 打印：
```bash
lp -d Brother_T725DW <file>
```
- 查看队列：
```bash
lpstat -o
```
- 查看指定任务：
```bash
lpstat -W not-completed
```

### Step 4 — 常见排障

#### 4.1 任务卡住/不出纸
1) 看队列：
```bash
lpstat -o
lpstat -p Brother_T725DW
```
2) 看是否暂停：
```bash
cupsenable Brother_T725DW || true
cupsaccept Brother_T725DW || true
```
3) 取消任务：
```bash
cancel Brother_T725DW-<JOBID>
# 或清空该队列
cancel -a Brother_T725DW
```

#### 4.2 “无系统默认目标”
设默认：
```bash
sudo lpadmin -d Brother_T725DW
```

#### 4.3 查看 CUPS 日志（需要权限）
```bash
sudo journalctl -u cups --no-pager -n 200
```

## 约定：本环境的打印机信息（非敏感）
- 机型：Brother DCP‑T725DW
- 建议队列名：`Brother_T725DW`
- Web 管理地址：`http://10.0.0.24/`（仅内网）
- 常用端口：80/443/631/515/9100

## Resources

### scripts/
- `scripts/print_file.sh`：统一入口（选择队列、打印、查看队列），支持试卷 PDF 自动去答案尾页。
- `scripts/prepare_pdf_for_print.sh`：试卷 PDF 预处理（基于关键词识别；优先 `pdftotext`，抽不出字时 OCR；使用 `gs` 裁剪尾页答案）。
- `scripts/ocr_pdf_pages.sh`：OCR 兜底（pdftoppm + tesseract，仅对少量页做 OCR）。

### references/
- `references/brother-dcp-t725dw.md`：设备专属参数与排障要点（不含密码）。
