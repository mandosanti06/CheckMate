import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../..");
const script = path.join(
  repoRoot,
  "skills",
  "checkmate-agent-system",
  "scripts",
  "checkmate_plan.py"
);

function runPython(args) {
  const attempts = [
    { command: "python3", args: [script, ...args] },
    { command: "python", args: [script, ...args] },
    { command: "py", args: ["-3", script, ...args] }
  ];

  for (const attempt of attempts) {
    const result = spawnSync(attempt.command, attempt.args, {
      cwd: repoRoot,
      encoding: "utf8"
    });
    if (result.error && result.error.code === "ENOENT") {
      continue;
    }
    return result;
  }
  throw new Error("No Python executable found for skill script test");
}

test("bundled skill script emits checkmate for direct contradictions", () => {
  const result = runPython([
    "--goal",
    "Ship integration",
    "--constraint",
    "must use external API",
    "--constraint",
    "cannot use external API",
    "--format",
    "json"
  ]);

  assert.equal(result.status, 0);
  const board = JSON.parse(result.stdout);
  assert.equal(board.status, "checkmate");
  assert.equal(board.conflicts.length, 1);
});

