---
name: openclaw-cmd-cn
description: OpenClaw 命令中文化套件。将内置命令描述翻译为中文，支持升级后自动汉化。当用户想要汉化 OpenClaw 命令、修改命令描述为中文、或提到"命令中文化"时使用。
---

# OpenClaw 命令中文化套件

将 OpenClaw 内置 `/` 命令的英文描述替换为中文，支持升级后自动执行。

## 快速开始

```bash
# 方式1: 升级 + 汉化一条龙（推荐）
python3 scripts/upgrade-openclaw.py

# 方式2: 仅汉化（不升级）
python3 scripts/translate-commands.py
```

## 自动化（可选）

安装 post-upgrade hooks，`npm update -g openclaw` 后自动汉化：

```bash
# 安装 hook 系统
node scripts/install-hooks.js

# 启用自动汉化 hook
cp examples/translate-commands ~/.openclaw/hooks/post-upgrade/
chmod +x ~/.openclaw/hooks/post-upgrade/translate-commands
```

之后每次 `npm update -g openclaw` 会自动运行汉化脚本。

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `scripts/upgrade-openclaw.py` | 升级 OpenClaw + 自动汉化 |
| `scripts/translate-commands.py` | 手动汉化 |
| `scripts/install-hooks.js` | 安装 post-upgrade hook 系统 |

## 常用命令

```bash
# 查看将要进行的更改（预览）
python3 scripts/translate-commands.py --dry-run

# 从备份恢复原文件
python3 scripts/translate-commands.py --restore

# 检查 OpenClaw 是否有更新
python3 scripts/upgrade-openclaw.py --check
```

## 注意

1. **更新后需重跑**：OpenClaw 更新会覆盖修改，需重新运行或使用 hooks 自动化
2. **自动备份**：首次运行会创建 `.backup` 文件
3. **仅描述翻译**：命令名称（如 `/status`）保持不变

## 维护指南

### 添加新翻译

当 OpenClaw 新增命令或发现遗漏时：

1. 运行 `--dry-run` 检查遗漏：
   ```bash
   python3 scripts/translate-commands.py --dry-run
   ```

2. 如果有英文描述未翻译，编辑 `scripts/translate-commands.py` 中的 `TRANSLATIONS` 字典，添加：
   ```python
   '"English description"': '"中文描述"',
   ```

3. 重新运行汉化：
   ```bash
   python3 scripts/translate-commands.py
   ```

### 扫描范围

脚本扫描以下文件：
- `dist/command-registry-*.js` - 主命令注册
- `dist/register*.js` - 子命令描述（重要！）
- `dist/*-cli-*.js` - 各命令的 CLI 文件
- `dist/program*.js` - 主程序
- `dist/plugin-sdk/commands-registry-*.js` - 插件 SDK

### 常见问题

**Q: 汉化后仍有英文？**

A: 描述可能在新文件中。检查 `openclaw --help` 输出，找到英文描述，然后在脚本中添加翻译。

**Q: OpenClaw 升级后汉化失效？**

A: 重新运行脚本即可。建议安装 post-upgrade hooks 实现自动化。

## 相关仓库

- GitHub: https://github.com/qq980251986-hash/openclaw-cmd-cn
