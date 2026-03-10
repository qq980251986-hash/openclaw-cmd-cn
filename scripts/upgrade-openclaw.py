#!/usr/bin/env python3
"""
OpenClaw 升级 + 自动汉化脚本

用法:
    python3 scripts/upgrade-openclaw.py          # 升级并汉化
    python3 scripts/upgrade-openclaw.py --check  # 仅检查更新
"""

import subprocess
import sys
import os
from pathlib import Path

def get_current_version():
    """获取当前 OpenClaw 版本"""
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return None

def get_latest_version():
    """获取 npm 上最新版本"""
    try:
        result = subprocess.run(
            ["npm", "view", "openclaw", "version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except Exception:
        return None

def upgrade_openclaw():
    """升级 OpenClaw"""
    print("⬆️  升级 OpenClaw...")
    result = subprocess.run(
        ["npm", "update", "-g", "openclaw"],
        timeout=120
    )
    return result.returncode == 0

def run_translation():
    """运行汉化脚本"""
    script_dir = Path(__file__).parent
    translate_script = script_dir / "translate-commands.py"
    
    if not translate_script.exists():
        print("❌ 找不到 translate-commands.py")
        return False
    
    print("\n🔧 运行汉化...")
    result = subprocess.run(
        [sys.executable, str(translate_script)],
        timeout=60
    )
    return result.returncode == 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description='OpenClaw 升级 + 自动汉化')
    parser.add_argument('--check', action='store_true', help='仅检查是否有更新')
    parser.add_argument('--no-translate', action='store_true', help='升级后不运行汉化')
    args = parser.parse_args()
    
    current = get_current_version()
    latest = get_latest_version()
    
    print(f"📌 当前版本: {current or '未知'}")
    print(f"🌐 最新版本: {latest or '未知'}")
    
    if args.check:
        if current and latest:
            if current < latest:
                print(f"\n✨ 有新版本可升级: {current} → {latest}")
            else:
                print("\n✅ 已是最新版本")
        return
    
    if current and latest and current >= latest:
        print("\n✅ 已是最新版本，无需升级")
        if not args.no_translate:
            run_translation()
        return
    
    # 升级
    if upgrade_openclaw():
        new_version = get_current_version()
        print(f"✓ 升级成功: {new_version}")
        
        if not args.no_translate:
            run_translation()
    else:
        print("❌ 升级失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
