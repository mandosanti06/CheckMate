import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SKILL_NAME = "checkmate-agent-system";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
export const PACKAGE_ROOT = path.resolve(__dirname, "..");
export const SKILL_SOURCE = path.join(PACKAGE_ROOT, "skills", SKILL_NAME);
export const SKILL_ZIP = path.join(PACKAGE_ROOT, "dist", `${SKILL_NAME}-skill.zip`);

export function defaultSkillRoot(target, cwd = process.cwd()) {
  if (target === "codex") {
    return path.join(process.env.CODEX_HOME || path.join(os.homedir(), ".codex"), "skills");
  }
  if (target === "claude") {
    return path.join(os.homedir(), ".claude", "skills");
  }
  if (target === "claude-project") {
    return path.join(cwd, ".claude", "skills");
  }
  throw new Error(`Unknown install target: ${target}`);
}

export function installSkill({ target, root, force = false, cwd = process.cwd() }) {
  const skillRoot = path.resolve(root || defaultSkillRoot(target, cwd));
  const destination = path.join(skillRoot, SKILL_NAME);

  assertSkillSource();
  fs.mkdirSync(skillRoot, { recursive: true });

  if (fs.existsSync(destination)) {
    if (!force) {
      return {
        installed: false,
        destination,
        message: `Skill already exists at ${destination}. Re-run with --force to replace it.`
      };
    }
    fs.rmSync(destination, { recursive: true, force: true });
  }

  fs.cpSync(SKILL_SOURCE, destination, { recursive: true });
  return {
    installed: true,
    destination,
    message: `Installed ${SKILL_NAME} to ${destination}`
  };
}

export function assertSkillSource() {
  const skillFile = path.join(SKILL_SOURCE, "SKILL.md");
  if (!fs.existsSync(skillFile)) {
    throw new Error(`Missing bundled skill at ${skillFile}`);
  }
}

export function doctor() {
  const checks = [
    {
      name: "bundled skill",
      ok: fs.existsSync(path.join(SKILL_SOURCE, "SKILL.md")),
      detail: SKILL_SOURCE
    },
    {
      name: "bundled zip",
      ok: fs.existsSync(SKILL_ZIP),
      detail: SKILL_ZIP
    },
    {
      name: "codex skills root",
      ok: fs.existsSync(defaultSkillRoot("codex")),
      detail: defaultSkillRoot("codex")
    },
    {
      name: "claude skills root",
      ok: fs.existsSync(defaultSkillRoot("claude")),
      detail: defaultSkillRoot("claude")
    }
  ];

  return checks;
}

