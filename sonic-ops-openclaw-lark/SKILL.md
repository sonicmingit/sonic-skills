---
name: sonic-ops-飞书插件运维
description: 当`npx -y @larksuite/openclaw-lark update`失败（如tgz解压超时）时，手动升级飞书/Lark官方OpenClaw插件（@larksuite/openclaw-lark）。提供安全、可重复的工作流程和内置shell脚本，用于npm-pack插件、备份/移动现有~/.openclaw/extensions/larksuite-openclaw-plugin文件夹、解压下载的.tgz，并验证（可选修补）~/.openclaw/openclaw.json的plugins.allow包含openclaw-lark。
---

# sonic-ops-飞书插件运维

Use this skill to perform a **manual** upgrade of the Feishu official plugin when the automated updater fails at extraction (timeout/slow IO).

## What this skill includes

- `scripts/update-openclaw-lark.sh`: one-shot updater (backup → download → extract → install → verify config)

## Location

Installed under:

- `/home/sonic/.openclaw/skills/sonic-ops-openclaw-lark/`

## Prereqs

- OpenClaw already installed (`openclaw -v`)
- `npm` available
- Write permission to `~/.openclaw/extensions`

## Recommended workflow (safe)

1) Check OpenClaw version

```bash
openclaw -v
```

2) Run the manual updater

```bash
bash /home/sonic/.openclaw/skills/sonic-ops-openclaw-lark/scripts/update-openclaw-lark.sh
```

Optional flags:

- Pin a version:

```bash
bash /home/sonic/.openclaw/skills/sonic-ops-openclaw-lark/scripts/update-openclaw-lark.sh --version 2026.3.17
```

- Auto-fix `plugins.allow` in `~/.openclaw/openclaw.json` (adds `openclaw-lark` if missing):

```bash
bash /home/sonic/.openclaw/skills/sonic-ops-openclaw-lark/scripts/update-openclaw-lark.sh --fix-plugins-allow
```

## What the script does (high level)

- Works in `~/.openclaw/extensions`
- Creates a timestamped backup by **moving** `larksuite-openclaw-plugin/` into `~/.openclaw/extensions/_backup/`
- `npm pack @larksuite/openclaw-lark[@version]` to download the `.tgz`
- Extracts the tgz into a temp dir and installs it as `larksuite-openclaw-plugin/`
- Prints a clear version summary (before → after) by reading `package.json`
- Verifies `~/.openclaw/openclaw.json` contains `plugins.allow: ["openclaw-lark", ...]`

## Safety notes

- The script avoids `rm -rf` by default; it uses **move-to-backup** for rollback.
- If anything fails after the backup move, you can restore by moving the backup folder back to `larksuite-openclaw-plugin/`.
