#!/usr/bin/env node
import fs from "node:fs";
import { buildBoard, formatText } from "../lib/plan.js";
import {
  SKILL_NAME,
  SKILL_SOURCE,
  SKILL_ZIP,
  defaultSkillRoot,
  doctor,
  installSkill
} from "../lib/skill.js";

const packageJson = JSON.parse(
  fs.readFileSync(new URL("../package.json", import.meta.url), "utf8")
);
const VERSION = packageJson.version;

function usage() {
  return `CheckMate Agent System ${VERSION}

Usage:
  checkmate plan --goal <goal> [--constraint <constraint>] [--format text|json]
  checkmate install codex|claude|claude-project [--path <skills-root>] [--force]
  checkmate skill-path
  checkmate zip-path
  checkmate doctor
  checkmate help

Examples:
  npx checkmate-agent-system@latest plan --goal "Build a migration plan" -c "must preserve uptime"
  npx checkmate-agent-system@latest install codex
  npx checkmate-agent-system@latest install claude --force
  npx checkmate-agent-system@latest install claude-project --path .claude/skills
`;
}

function parseArgs(argv) {
  const options = { _: [], constraint: [] };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--") {
      options._.push(...argv.slice(index + 1));
      break;
    }
    if (arg.startsWith("--")) {
      const [rawKey, inlineValue] = arg.slice(2).split("=", 2);
      const key = rawKey.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
      if (key === "force" || key === "json" || key === "help" || key === "version") {
        options[key] = true;
        continue;
      }
      const value = inlineValue ?? argv[index + 1];
      if (inlineValue === undefined) index += 1;
      if (value === undefined) throw new Error(`Missing value for --${rawKey}`);
      if (key === "constraint") {
        options.constraint.push(value);
      } else {
        options[key] = value;
      }
      continue;
    }
    if (arg === "-c") {
      const value = argv[index + 1];
      if (value === undefined) throw new Error("Missing value for -c");
      options.constraint.push(value);
      index += 1;
      continue;
    }
    if (arg === "-g") {
      const value = argv[index + 1];
      if (value === undefined) throw new Error("Missing value for -g");
      options.goal = value;
      index += 1;
      continue;
    }
    if (arg === "-h") {
      options.help = true;
      continue;
    }
    options._.push(arg);
  }

  return options;
}

function runPlan(options) {
  if (!options.goal) {
    throw new Error("plan requires --goal <goal>");
  }

  const board = buildBoard(options.goal, options.constraint);
  const format = options.json ? "json" : options.format || "text";
  if (!["text", "json"].includes(format)) {
    throw new Error("--format must be text or json");
  }

  if (format === "json") {
    console.log(JSON.stringify(board, null, 2));
  } else {
    console.log(formatText(board));
  }
}

function runInstall(target, options) {
  if (!target) {
    throw new Error("install requires codex, claude, or claude-project");
  }
  if (!["codex", "claude", "claude-project"].includes(target)) {
    throw new Error(`Unknown install target: ${target}`);
  }

  const result = installSkill({
    target,
    root: options.path,
    force: Boolean(options.force)
  });

  console.log(result.message);
  if (!result.installed) process.exitCode = 2;
}

function runDoctor() {
  console.log(`CheckMate Agent System ${VERSION}`);
  for (const check of doctor()) {
    const mark = check.ok ? "OK" : "MISSING";
    console.log(`${mark.padEnd(7)} ${check.name}: ${check.detail}`);
  }
  console.log(`INFO    default Codex target: ${defaultSkillRoot("codex")}`);
  console.log(`INFO    default Claude target: ${defaultSkillRoot("claude")}`);
}

function main(argv = process.argv.slice(2)) {
  const [command, ...rest] = argv;
  const options = parseArgs(rest);

  if (!command || command === "help" || options.help) {
    console.log(usage());
    return;
  }
  if (command === "--version" || command === "version" || options.version) {
    console.log(VERSION);
    return;
  }
  if (command === "plan") {
    runPlan(options);
    return;
  }
  if (command === "install") {
    runInstall(options._[0], options);
    return;
  }
  if (command === "skill-path") {
    console.log(SKILL_SOURCE);
    return;
  }
  if (command === "zip-path") {
    if (!fs.existsSync(SKILL_ZIP)) {
      throw new Error(`Bundled zip not found at ${SKILL_ZIP}`);
    }
    console.log(SKILL_ZIP);
    return;
  }
  if (command === "doctor") {
    runDoctor();
    return;
  }

  throw new Error(`Unknown command: ${command}\n\n${usage()}`);
}

try {
  main();
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`checkmate: ${message}`);
  process.exitCode = 1;
}

export { main, usage };
