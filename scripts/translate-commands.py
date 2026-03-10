#!/usr/bin/env python3
"""
OpenClaw 命令描述中文化脚本

将 OpenClaw 内置命令的英文描述替换为中文。
注意：每次 OpenClaw 更新后需要重新运行此脚本。
"""

import os
import re
import sys
import glob
import shutil
from pathlib import Path

# 英文 -> 中文 翻译映射
TRANSLATIONS = {
    # 命令描述
    '"Show or set config values."': '"显示或设置配置值。"',
    '"Set runtime debug overrides."': '"设置运行时调试覆盖。"',
    '"Set group activation mode."': '"设置群组激活模式。"',
    '"Set send policy."': '"设置发送策略。"',
    '"Show or set the model."': '"显示或设置模型。"',
    '"Run host shell commands (host-only)."': '"运行主机 Shell 命令（仅限主机）。"',
    '"Remove the current thread (Discord) or topic/conversation (Telegram) binding."': '"移除当前线程（Discord）或主题/会话（Telegram）绑定。"',
    '"List thread-bound agents for this session."': '"列出此会话的线程绑定代理。"',
    '"Send guidance to a running subagent."': '"向运行中的子代理发送指导。"',
    
    # 参数描述
    '"show | get | set | unset"': '"show | get | set | unset（显示|获取|设置|取消）"',
    '"Config path"': '"配置路径"',
    '"Value for set"': '"设置的值"',
    '"show | reset | set | unset"': '"show | reset | set | unset（显示|重置|设置|取消）"',
    '"Debug path"': '"调试路径"',
    '"mention or always"': '"mention（提及）或 always（始终）"',
    '"on, off, or inherit"': '"on（开）、off（关）或 inherit（继承）"',
    '"Model id (provider/model or id)"': '"模型 ID（provider/model 或 id）"',
    '"Shell command"': '"Shell 命令"',
    '"Action to run"': '"要运行的操作"',
    '"Action arguments"': '"操作参数"',
    '"Subagent label/index or session key/id/label"': '"子代理标签/索引或会话 key/id/标签"',
    '"Label, run id, or index"': '"标签、运行 ID 或索引"',
    '"Steering message"': '"指导消息"',
    '"Label, run id, index, or all"': '"标签、运行 ID、索引或 all（全部）"',
    '"sandbox, gateway, or node"': '"sandbox（沙盒）、gateway（网关）或 node（节点）"',
    '"deny, allowlist, or full"': '"deny（拒绝）、allowlist（白名单）或 full（完全）"',
    '"off, on-miss, or always"': '"off（关）、on-miss（未命中时）或 always（始终）"',
    '"Node id or name"': '"节点 ID 或名称"',
    '"queue mode"': '"队列模式"',
    '"debounce duration (e.g. 500ms, 2s)"': '"防抖时长（如 500ms、2s）"',
    '"queue cap"': '"队列上限"',
    '"drop policy"': '"丢弃策略"',
    
    # Skill 相关
    '"Skill name"': '"技能名称"',
    '"Skill input"': '"技能输入"',
    
    # TTS 相关
    '"TTS action"': '"TTS 操作"',
    '"Provider, limit, or text"': '"提供商、限制或文本"',
    
    # 其他
    '"Output path (default: workspace)"': '"输出路径（默认：workspace）"',
    '"Extra compaction instructions"': '"额外压缩指令"',
    '"off, tokens, full, or cost"': '"off（关）、tokens（词元）、full（完整）或 cost（成本）"',
    '"on or off"': '"on（开）或 off（关）"',
    '"on, off, or stream"': '"on（开）、off（关）或 stream（流式）"',
    '"on, off, ask, or full"': '"on（开）、off（关）、ask（询问）或 full（完全）"',
    '"off, minimal, low, medium, high, xhigh"': '"off（关）、minimal（最小）、low（低）、medium（中）、high（高）、xhigh（极高）"',
    '"idle | max-age"': '"idle（空闲）| max-age（最大时长）"',
    '"Duration (24h, 90m) or off"': '"时长（24h、90m）或 off（关）"',
    '"list | kill | log | info | send | steer | spawn"': '"list（列表）| kill（终止）| log（日志）| info（信息）| send（发送）| steer（引导）| spawn（生成）"',
    '"Run id, index, or session key"': '"运行 ID、索引或会话 key"',
    '"Additional input (limit/message)"': '"额外输入（limit/message）"',
}

def find_openclaw_dist():
    """查找 OpenClaw 安装目录"""
    # 尝试常见的安装位置
    candidates = [
        os.path.expanduser("~/.nvm/versions/node/*/lib/node_modules/openclaw/dist"),
        "/usr/local/lib/node_modules/openclaw/dist",
        "/usr/lib/node_modules/openclaw/dist",
    ]
    
    for pattern in candidates:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    
    return None

def find_commands_registry(dist_path):
    """查找 commands-registry JS 文件"""
    pattern = os.path.join(dist_path, "commands-registry-*.js")
    files = glob.glob(pattern)
    return files

def backup_file(filepath):
    """备份原文件"""
    backup_path = filepath + ".backup"
    if not os.path.exists(backup_path):
        shutil.copy2(filepath, backup_path)
        print(f"✓ 已备份: {backup_path}")
    return backup_path

def restore_file(filepath):
    """从备份恢复"""
    backup_path = filepath + ".backup"
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, filepath)
        print(f"✓ 已恢复: {filepath}")
        return True
    return False

def translate_file(filepath, dry_run=False):
    """翻译文件中的英文描述"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes = []
    for en, zh in TRANSLATIONS.items():
        if en in content:
            count = content.count(en)
            changes.append((en, zh, count))
            if not dry_run:
                content = content.replace(en, zh)
    
    if dry_run:
        return changes
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return changes

def main():
    import argparse
    parser = argparse.ArgumentParser(description='OpenClaw 命令描述中文化')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要进行的更改')
    parser.add_argument('--restore', action='store_true', help='从备份恢复原文件')
    parser.add_argument('--dist', type=str, help='指定 OpenClaw dist 目录')
    args = parser.parse_args()
    
    # 查找 dist 目录
    if args.dist:
        dist_path = args.dist
    else:
        dist_path = find_openclaw_dist()
    
    if not dist_path:
        print("❌ 找不到 OpenClaw 安装目录")
        print("   请使用 --dist 参数指定路径")
        sys.exit(1)
    
    print(f"📁 OpenClaw dist: {dist_path}")
    
    # 查找 commands-registry 文件
    registry_files = find_commands_registry(dist_path)
    if not registry_files:
        print("❌ 找不到 commands-registry-*.js 文件")
        sys.exit(1)
    
    print(f"📄 找到 {len(registry_files)} 个 registry 文件")
    
    if args.restore:
        # 恢复模式
        for filepath in registry_files:
            restore_file(filepath)
        print("\n✓ 恢复完成")
        return
    
    # 翻译模式
    total_changes = 0
    for filepath in registry_files:
        print(f"\n处理: {os.path.basename(filepath)}")
        
        if not args.dry_run:
            backup_file(filepath)
        
        changes = translate_file(filepath, dry_run=args.dry_run)
        
        if changes:
            for en, zh, count in changes:
                print(f"  [{count}x] {en[:50]}... → {zh[:50]}...")
                total_changes += count
        else:
            print("  (无需更改)")
    
    if args.dry_run:
        print(f"\n📊 共 {total_changes} 处可翻译")
    else:
        print(f"\n✓ 翻译完成，共 {total_changes} 处")
        print("⚠️  注意：OpenClaw 更新后需要重新运行此脚本")

if __name__ == "__main__":
    main()
