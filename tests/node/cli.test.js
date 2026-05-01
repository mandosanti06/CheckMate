import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../..");
const cli = path.join(repoRoot, "bin", "checkmate.js");

function run(args) {
  return execFileSync(process.execPath, [cli, ...args], {
    cwd: repoRoot,
    encoding: "utf8"
  });
}

test("cli prints version", () => {
  const output = run(["--version"]).trim();

  assert.match(output, /^\d+\.\d+\.\d+/);
});

test("cli prints help", () => {
  const output = run(["help"]);

  assert.match(output, /Usage:/);
  assert.match(output, /checkmate plan/);
});

test("cli emits json plan with checkmate conflict", () => {
  const output = run([
    "plan",
    "--goal=Ship integration",
    "--constraint",
    "must use external API",
    "--constraint",
    "cannot use external API",
    "--format",
    "json"
  ]);
  const board = JSON.parse(output);

  assert.equal(board.status, "checkmate");
  assert.equal(board.conflicts.length, 1);
});

test("cli installs skill to custom root", () => {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "checkmate-cli-"));
  const output = run(["install", "codex", "--path", tempRoot]);

  assert.match(output, /Installed checkmate-agent-system/);
  assert.ok(fs.existsSync(path.join(tempRoot, "checkmate-agent-system", "SKILL.md")));
});

test("cli returns exit code 2 when install already exists", () => {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "checkmate-cli-"));
  run(["install", "codex", "--path", tempRoot]);
  const result = spawnSync(
    process.execPath,
    [cli, "install", "codex", "--path", tempRoot],
    { cwd: repoRoot, encoding: "utf8" }
  );

  assert.equal(result.status, 2);
  assert.match(result.stdout, /already exists/);
});

test("cli supports install --force", () => {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "checkmate-cli-"));
  run(["install", "codex", "--path", tempRoot]);
  const output = run(["install", "codex", "--path", tempRoot, "--force"]);

  assert.match(output, /Installed checkmate-agent-system/);
});

test("cli rejects unknown commands", () => {
  const result = spawnSync(process.execPath, [cli, "unknown"], {
    cwd: repoRoot,
    encoding: "utf8"
  });

  assert.equal(result.status, 1);
  assert.match(result.stderr, /Unknown command/);
});
