#!/usr/bin/env node
/**
 * OpenClaw Post-Upgrade Hooks Installer
 *
 * 将 hook runner 注入到 OpenClaw 安装目录的 package.json 中
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const HOOKS_DIR = path.join(require('os').homedir(), '.openclaw', 'hooks', 'post-upgrade');

// 查找 OpenClaw 安装路径
function findOpenClaw() {
  const paths = [
    process.env.NVM_INC ? path.join(process.env.NVM_INC, 'openclaw') : null,
    '/usr/local/lib/node_modules/openclaw',
    '/usr/lib/node_modules/openclaw',
  ].filter(Boolean);

  for (const p of paths) {
    if (fs.existsSync(path.join(p, 'package.json'))) {
      return p;
    }
  }

  // 通过 npm root 查找
  try {
    const npmRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
    const openclawPath = path.join(npmRoot, 'openclaw');
    if (fs.existsSync(path.join(openclawPath, 'package.json'))) {
      return openclawPath;
    }
  } catch (e) {}

  return null;
}

// 复制 hook runner 脚本
function installHookRunner(openclawPath) {
  const scriptsDir = path.join(openclawPath, 'scripts');
  const destFile = path.join(scriptsDir, 'run-postinstall-hooks.mjs');
  const srcFile = path.join(__dirname, 'run-postinstall-hooks.mjs');

  if (!fs.existsSync(scriptsDir)) {
    fs.mkdirSync(scriptsDir, { recursive: true });
  }

  fs.copyFileSync(srcFile, destFile);
  console.log(`✅ 已安装: ${destFile}`);
  return destFile;
}

// 修改 package.json 添加 postinstall 脚本
function patchPackageJson(openclawPath) {
  const pkgPath = path.join(openclawPath, 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

  // 检查是否已安装
  if (pkg.scripts && pkg.scripts.postinstall === 'node scripts/run-postinstall-hooks.mjs') {
    console.log('✓ postinstall hook 已存在，跳过');
    return false;
  }

  // 备份原文件
  fs.copyFileSync(pkgPath, pkgPath + '.backup');
  console.log(`📦 备份: ${pkgPath}.backup`);

  // 添加 postinstall 脚本
  pkg.scripts = pkg.scripts || {};
  pkg.scripts.postinstall = 'node scripts/run-postinstall-hooks.mjs';

  fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2));
  console.log(`✅ 已修改: ${pkgPath}`);
  return true;
}

// 创建 hooks 目录
function ensureHooksDir() {
  if (!fs.existsSync(HOOKS_DIR)) {
    fs.mkdirSync(HOOKS_DIR, { recursive: true });
    console.log(`📁 创建: ${HOOKS_DIR}`);
  } else {
    console.log(`📁 Hooks 目录: ${HOOKS_DIR}`);
  }
}

function main() {
  console.log('🔧 OpenClaw Post-Upgrade Hooks 安装器\n');

  const openclawPath = findOpenClaw();
  if (!openclawPath) {
    console.error('❌ 未找到 OpenClaw 安装');
    console.log('请先安装: npm install -g openclaw');
    process.exit(1);
  }

  console.log(`📁 OpenClaw 路径: ${openclawPath}\n`);

  // 1. 安装 hook runner
  installHookRunner(openclawPath);

  // 2. 修改 package.json
  patchPackageJson(openclawPath);

  // 3. 创建 hooks 目录
  ensureHooksDir();

  console.log('\n✅ 安装完成！');
  console.log('\n使用方法:');
  console.log('  1. 将可执行脚本放入 ~/.openclaw/hooks/post-upgrade/');
  console.log('  2. npm update -g openclaw 时会自动运行');
  console.log('\n示例 hook: https://github.com/qq980251986-hash/openclaw-cmd-cn');
}

main();
