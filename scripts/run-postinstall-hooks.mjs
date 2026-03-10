#!/usr/bin/env node
/**
 * OpenClaw Postinstall Hooks Runner
 *
 * Runs user-defined scripts from ~/.openclaw/hooks/post-upgrade/
 * after npm install/upgrade.
 */

import { stat, readdir, chmod } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';
import { spawn } from 'node:child_process';

const HOOKS_DIR = join(homedir(), '.openclaw', 'hooks', 'post-upgrade');

async function isExecutable(filepath) {
  try {
    const s = await stat(filepath);
    return s.isFile() && (s.mode & 0o111); // has execute bit
  } catch {
    return false;
  }
}

async function runHook(hookPath, logPrefix) {
  return new Promise((resolve) => {
    const child = spawn(hookPath, [], {
      stdio: 'inherit',
      shell: false,
      timeout: 60000, // 60s timeout
    });

    child.on('error', (err) => {
      console.error(`${logPrefix} Error:`, err.message);
      resolve(false);
    });

    child.on('exit', (code) => {
      if (code !== 0) {
        console.error(`${logPrefix} Exited with code ${code}`);
        resolve(false);
      } else {
        console.log(`${logPrefix} ✓ Done`);
        resolve(true);
      }
    });
  });
}

async function main() {
  // Check if hooks directory exists
  try {
    await stat(HOOKS_DIR);
  } catch {
    // No hooks directory, silently exit
    process.exit(0);
  }

  // Get all files in hooks directory
  let files;
  try {
    files = await readdir(HOOKS_DIR);
  } catch {
    process.exit(0);
  }

  // Filter to executable files, sort alphabetically
  const hooks = [];
  for (const file of files) {
    const filepath = join(HOOKS_DIR, file);
    if (await isExecutable(filepath)) {
      hooks.push({ name: file, path: filepath });
    }
  }

  if (hooks.length === 0) {
    process.exit(0);
  }

  console.log(`\n🔧 Running ${hooks.length} post-upgrade hook(s)...\n`);

  for (const hook of hooks) {
    console.log(`📌 ${hook.name}`);
    await runHook(hook.path, `   `);
  }

  console.log('\n✓ Post-upgrade hooks complete\n');
}

main().catch((err) => {
  console.error('Postinstall hooks error:', err.message);
  process.exit(0); // Don't fail install on hook error
});
