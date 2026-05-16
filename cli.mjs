#!/usr/bin/env node
// Installer for the interior-design skill.
//
// Usage:
//   npx github:zyliu0/interior-design [options]
//   npx interior-design-skill@latest [options]    (after npm publish)
//
// Options:
//   --target, -t <dir>   Install destination (default: ~/.claude/skills/interior-design)
//   --codex              Shortcut for ~/.codex/skills/interior-design
//   --force, -f          Overwrite the target directory if it already exists
//   --help, -h           Show this help

import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));

// Files and directories to copy from this repo into the install target.
const PAYLOAD = [
  "SKILL.md",
  "README.md",
  "LICENSE",
  "requirements.txt",
  ".env.example",
  "package.json",
  "cli.mjs",
  "prompts",
  "references",
  "scripts",
];

function printHelp() {
  console.log(`
Installs the interior-design skill into your Claude Code (or Codex) skills directory.

Usage:
  npx github:zyliu0/interior-design [options]

Options:
  --target, -t <dir>   Install destination
                       (default: ~/.claude/skills/interior-design)
  --codex              Shortcut for ~/.codex/skills/interior-design
  --force, -f          Overwrite the target if it already exists
  --help, -h           Show this help

After install, invoke /interior-design in your AI host. For text-only hosts
(Claude Code, etc.) you'll also want to install Python deps and set up an
API key — the install script will print the next steps.
`);
}

function parseArgs(argv) {
  const opts = { target: null, force: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--target" || a === "-t") {
      const next = argv[++i];
      if (!next) {
        console.error("ERROR: --target requires a value");
        process.exit(2);
      }
      opts.target = resolve(next);
    } else if (a === "--codex") {
      opts.target = join(homedir(), ".codex", "skills", "interior-design");
    } else if (a === "--force" || a === "-f") {
      opts.force = true;
    } else if (a === "--help" || a === "-h") {
      printHelp();
      process.exit(0);
    } else {
      console.error(`ERROR: unknown argument: ${a}`);
      console.error("Run with --help for usage.");
      process.exit(2);
    }
  }
  if (!opts.target) {
    opts.target = join(homedir(), ".claude", "skills", "interior-design");
  }
  return opts;
}

function main() {
  const { target, force } = parseArgs(process.argv.slice(2));

  if (existsSync(target)) {
    if (!force) {
      console.error(`ERROR: target already exists: ${target}`);
      console.error("Re-run with --force to overwrite, or pass --target <other-dir>.");
      process.exit(1);
    }
    rmSync(target, { recursive: true, force: true });
  }

  mkdirSync(target, { recursive: true });

  let copied = 0;
  for (const name of PAYLOAD) {
    const src = join(SCRIPT_DIR, name);
    if (!existsSync(src)) continue;
    cpSync(src, join(target, name), { recursive: true });
    copied++;
  }

  if (copied === 0) {
    console.error("ERROR: no files copied. Is the script running from the wrong directory?");
    console.error(`Looked in: ${SCRIPT_DIR}`);
    process.exit(3);
  }

  console.log(`✓ Installed interior-design skill to ${target}`);
  console.log("");
  console.log("Next steps:");
  console.log(`  cd ${target}`);
  console.log("");
  console.log("  # Mode A (Codex, Gemini app, any native multi-modal host):");
  console.log("  # You're done. Invoke /interior-design in your host.");
  console.log("");
  console.log("  # Mode B (Claude Code, text-only hosts):");
  console.log("  pip install -r requirements.txt");
  console.log("  cp .env.example .env");
  console.log("  # Then edit .env and add GEMINI_API_KEY or OPENAI_API_KEY.");
  console.log("");
  console.log("Docs: https://github.com/zyliu0/interior-design");
}

main();
