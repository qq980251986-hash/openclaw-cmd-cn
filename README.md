# OpenClaw 命令中文化

将 OpenClaw 内置 `/` 命令的英文描述替换为中文。

## 安装

```bash
# 克隆仓库
git clone https://github.com/qq980251986-hash/openclaw-cmd-cn.git
cd openclaw-cmd-cn

# 或通过 ClawHub
clawhub install openclaw-cmd-cn
```

## 使用方法

```bash
# 查看将要进行的更改（预览模式）
python3 scripts/translate-commands.py --dry-run

# 执行翻译
python3 scripts/translate-commands.py

# 从备份恢复原文件
python3 scripts/translate-commands.py --restore
```

## 注意事项

1. **更新后需重跑**：OpenClaw 每次更新会覆盖修改，需重新运行脚本
2. **自动备份**：首次运行会创建 `.backup` 文件
3. **仅描述翻译**：命令名称（如 `/status`）保持不变

## 翻译内容

| 类型 | 示例 |
|------|------|
| 命令描述 | "Show or set config values." → "显示或设置配置值。" |
| 参数说明 | "Config path" → "配置路径" |
| 选项值 | "on or off" → "on（开）或 off（关）" |

## 手动添加翻译

编辑 `scripts/translate-commands.py` 中的 `TRANSLATIONS` 字典：

```python
TRANSLATIONS = {
    '"English text"': '"中文文本"',
    # 添加更多...
}
```

## License

MIT
