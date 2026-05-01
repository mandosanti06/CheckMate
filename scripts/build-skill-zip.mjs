import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");
const skillsDir = path.join(repoRoot, "skills");
const skillName = "checkmate-agent-system";
const distDir = path.join(repoRoot, "dist");
const destZip = path.join(distDir, `${skillName}-skill.zip`);

if (!fs.existsSync(path.join(skillsDir, skillName))) {
  console.error(`Source not found: ${path.join(skillsDir, skillName)}`);
  process.exit(1);
}

fs.mkdirSync(distDir, { recursive: true });
if (fs.existsSync(destZip)) {
  fs.rmSync(destZip);
}

const attempts = [
  { command: "python3", args: ["-m", "zipfile", "-c", destZip, skillName] },
  { command: "python", args: ["-m", "zipfile", "-c", destZip, skillName] },
  { command: "py", args: ["-3", "-m", "zipfile", "-c", destZip, skillName] }
];

let built = false;
for (const attempt of attempts) {
  const result = spawnSync(attempt.command, attempt.args, {
    cwd: skillsDir,
    stdio: "inherit"
  });
  if (result.error && result.error.code === "ENOENT") {
    continue;
  }
  if (result.error) {
    throw result.error;
  }
  if (result.status === 0) {
    built = true;
    break;
  }
  process.exit(result.status ?? 1);
}

if (!built) {
  console.error("Could not find a Python executable. Tried python3, python, and py -3.");
  process.exit(1);
}

const { size } = fs.statSync(destZip);
console.log(`Built dist/${skillName}-skill.zip (${size} bytes)`);
