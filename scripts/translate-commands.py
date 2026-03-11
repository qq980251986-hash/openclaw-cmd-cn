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
    # CLI 主命令描述
    '"Display help for command"': '"显示命令帮助"',
    '"output the version number"': '"输出版本号"',
    '"Non-interactive config helpers (get/set/unset/file/validate). Default: starts setup wizard."': '"非交互式配置助手（get/set/unset/file/validate）。默认：启动设置向导。"',
    '"Non-interactive config helpers (get/set/unset/file/validate). Run without subcommand for the setup wizard."': '"非交互式配置助手（get/set/unset/file/validate）。不带子命令运行启动设置向导。"',
    '"Configure wizard sections (repeatable). Use with no subcommand."': '"配置向导部分（可重复）。不带子命令使用。"',
    '"Print the active config file path"': '"打印当前配置文件路径"',
    '"Get a config value by dot path"': '"通过点路径获取配置值"',
    '"Set a config value by dot path"': '"通过点路径设置配置值"',
    '"Remove a config value by dot path"': '"通过点路径移除配置值"',
    '"Validate the current config against the schema without starting the gateway"': '"验证配置文件，不启动网关"',
    '"Manage connected chat channels (Telegram, Discord, etc.)"': '"管理聊天频道（Telegram、Discord 等）"',
    '"Manage OpenClaw\'s dedicated browser (Chrome/Chromium)"': '"管理 OpenClaw 专用浏览器"',
    '"Run one agent turn via the Gateway"': '"通过网关运行一个代理回合"',
    '"Manage isolated agents (workspaces, auth, routing)"': '"管理隔离代理（工作区、认证、路由）"',
    '"Generate shell completion script"': '"生成 Shell 补全脚本"',
    '"Agent Control Protocol tools"': '"代理控制协议工具"',
    '"Manage exec approvals (gateway or node host)"': '"管理执行审批（网关或节点主机）"',
    '"Legacy clawbot command aliases"': '"旧版 clawbot 命令别名"',
    '"Interactive setup wizard for credentials, channels, gateway, and agent defaults"': '"交互式设置向导"',
    '"Manage cron jobs via the Gateway scheduler"': '"管理定时任务"',
    '"Gateway service (legacy alias)"': '"网关服务（旧版别名）"',
    '"Open the Control UI with your current token"': '"打开控制面板"',
    '"Device pairing + token management"': '"设备配对和令牌管理"',
    '"Lookup contact and group IDs (self, peers, groups) for supported chat channels"': '"查找联系人/群组 ID"',
    '"DNS helpers for wide-area discovery (Tailscale + CoreDNS)"': '"DNS 发现助手（Tailscale + CoreDNS）"',
    '"Search the live OpenClaw docs"': '"搜索 OpenClaw 文档"',
    '"Health checks + quick fixes for the gateway and channels"': '"网关和频道健康检查"',

    # command-registry 主命令
    '"Initialize local config and agent workspace"': '"初始化本地配置和代理工作区"',
    '"Interactive onboarding wizard for gateway, workspace, and skills"': '"网关、工作区和技能的交互式入门向导"',
    '"Reset local config/state (keeps the CLI installed)"': '"重置本地配置/状态（保留 CLI）"',
    '"Uninstall the gateway service + local data (CLI remains)"': '"卸载网关服务和本地数据（保留 CLI）"',
    '"Send, read, and manage messages"': '"发送、读取和管理消息"',
    '"Search and reindex memory files"': '"搜索和重建记忆文件索引"',
    '"Show channel health and recent session recipients"': '"显示频道健康状态和最近会话接收者"',
    '"List stored conversation sessions"': '"列出存储的会话"',

    # 其他命令描述
    '"Manage internal agent hooks"': '"管理内部代理钩子"',
    '"Tail gateway file logs via RPC"': '"通过 RPC 追踪网关日志"',
    '"Discover, scan, and configure models"': '"发现、扫描和配置模型"',
    '"Run and manage the headless node host service"': '"运行和管理无头节点主机服务"',
    '"Manage gateway-owned node pairing and node commands"': '"管理网关节点配对和节点命令"',
    '"Generate iOS pairing QR/setup code"': '"生成 iOS 配对二维码/设置代码"',
    '"Manage sandbox containers for agent isolation"': '"管理代理隔离沙盒容器"',
    '"Secrets runtime reload controls"': '"密钥运行时重载控制"',
    '"Security tools and local config audits"': '"安全工具和本地配置审计"',
    '"List and inspect available skills"': '"列出和检查可用技能"',
    '"System events, heartbeat, and presence"': '"系统事件、心跳和在线状态"',
    '"Open a terminal UI connected to the Gateway"': '"打开连接到网关的终端界面"',
    '"Manage OpenClaw plugins and extensions"': '"管理 OpenClaw 插件和扩展"',
    '"Webhook helpers and integrations"': '"Webhook 助手和集成"',
    '"Update OpenClaw and inspect update channel status"': '"更新 OpenClaw 并检查更新通道状态"',
    '"Secure DM pairing (approve inbound requests)"': '"安全私信配对（批准入站请求）"',
    '"output the version number"': '"输出版本号"',

    # 选项描述
    '"Dev profile: isolate state under ~/.openclaw-dev, default gateway port 19001, and shift derived ports (browser/canvas)"': '"开发配置：隔离状态到 ~/.openclaw-dev，默认网关端口 19001，并调整衍生端口（浏览器/画布）"',
    '"Global log level override for file + console (silent|fatal|error|warn|info|debug|trace)"': '"全局日志级别覆盖（silent|fatal|error|warn|info|debug|trace）"',

    # 动态拼接的描述（带变量）
    '`Global log level override for file + console (${CLI_LOG_LEVEL_VALUES})`': '"全局日志级别覆盖（silent|fatal|error|warn|info|debug|trace）"',
    '"Run, inspect, and query the WebSocket Gateway"': '"运行、检查和查询 WebSocket 网关"',
    '"Fetch health from the running gateway"': '"获取运行中网关的健康状态"',
    '"Disable ANSI colors"': '"禁用 ANSI 颜色"',
    
    # plugin-sdk 命令描述
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
    """查找 OpenClaw 安装目录（支持 npm 和 bun）"""
    # 尝试常见的安装位置
    candidates = [
        # bun 全局安装
        os.path.expanduser("~/.bun/install/global/node_modules/openclaw/dist"),
        # npm/nvm 安装
        os.path.expanduser("~/.nvm/versions/node/*/lib/node_modules/openclaw/dist"),
        "/usr/local/lib/node_modules/openclaw/dist",
        "/usr/lib/node_modules/openclaw/dist",
    ]
    
    for pattern in candidates:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    
    return None

def find_js_files(dist_path):
    """查找所有需要翻译的 JS 文件"""
    files = []
    # plugin-sdk 目录下的文件（主要文件）
    sdk_path = os.path.join(dist_path, "plugin-sdk")
    if os.path.exists(sdk_path):
        for pattern in ["commands-registry-*.js"]:
            files.extend(glob.glob(os.path.join(sdk_path, pattern)))
    # dist/ 目录下的文件（辅助文件）
    for pattern in [
        "command-registry-*.js",
        "config-cli-*.js",
        "program*.js",
        "index.js",
        "program-context*.js",
        # 各命令的 CLI 文件
        "*-cli-*.js",
        # register 文件（包含子命令描述）
        "register*.js",
    ]:
        files.extend(glob.glob(os.path.join(dist_path, pattern)))
    return sorted(set(files))

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
    
    # 翻译 description 字段中的文本
    # 匹配 description: "..." 或 description: '...'
    import re
    desc_pattern = re.compile(r'description:\s*["\']([^"\']*)["\']')
    matches = desc_pattern.findall(content)
    
    for en_desc in matches:
        # 检查是否在 TRANSLATIONS 中有对应翻译
        for en, zh in TRANSLATIONS.items():
            if en_desc == en:
                # 找到了匹配，需要替换
                # 使用更精确的正则来替换整个 description 行
                new_pattern = re.compile(r'description:\s*["\']' + re.escape(en) + r'["\']')
                replacement = f'description: "{zh}"' if not content.split(en_desc)[0][-1].isalnum() else f"description: \'{zh}\'"
                
                if not dry_run:
                    new_content = new_pattern.sub(replacement, content, count=1)
                    if new_content != content:
                        changes.append((en, zh, 1))
                        content = new_content
    
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
    
    # 查找需要翻译的 JS 文件
    js_files = find_js_files(dist_path)
    if not js_files:
        print("❌ 找不到需要翻译的 JS 文件")
        sys.exit(1)
    
    print(f"📄 找到 {len(js_files)} 个文件")
    
    if args.restore:
        # 恢复模式
        for filepath in js_files:
            restore_file(filepath)
        print("\n✓ 恢复完成")
        return
    
    # 翻译模式
    total_changes = 0
    for filepath in js_files:
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
