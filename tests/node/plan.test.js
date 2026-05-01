import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { buildBoard, findConstraintContradiction, formatText } from "../../lib/plan.js";
import { installSkill } from "../../lib/skill.js";

test("buildBoard creates CheckMate roles and constraints", () => {
  const board = buildBoard("Ship a package", ["must support npx"]);

  assert.equal(board.goal, "Ship a package");
  assert.equal(board.constraints[0].description, "must support npx");
  assert.ok(board.active_agents.includes("king"));
  assert.ok(board.active_agents.includes("pawn_qa"));
  assert.ok(board.tasks.some((task) => task.id === "rooks_validate"));
});

test("formatText renders a concise brief", () => {
  const board = buildBoard("Plan a release", ["no downtime"]);
  const text = formatText(board);

  assert.match(text, /King: Plan a release/);
  assert.match(text, /Rooks: validate hard constraints/);
});

test("installSkill copies bundled skill", () => {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "checkmate-skill-"));
  const result = installSkill({ target: "codex", root: tempRoot });

  assert.equal(result.installed, true);
  assert.ok(fs.existsSync(path.join(result.destination, "SKILL.md")));
});

test("installSkill refuses to overwrite without force", () => {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "checkmate-skill-"));
  installSkill({ target: "codex", root: tempRoot });
  const result = installSkill({ target: "codex", root: tempRoot });

  assert.equal(result.installed, false);
  assert.match(result.message, /--force/);
});

test("installSkill replaces existing install with force", () => {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "checkmate-skill-"));
  const first = installSkill({ target: "codex", root: tempRoot });
  const marker = path.join(first.destination, "marker.txt");
  fs.writeFileSync(marker, "stale");

  const second = installSkill({ target: "codex", root: tempRoot, force: true });

  assert.equal(second.installed, true);
  assert.equal(fs.existsSync(marker), false);
  assert.ok(fs.existsSync(path.join(second.destination, "SKILL.md")));
});

test("buildBoard with no contradiction stays in planning status", () => {
  const board = buildBoard("Ship a thing", ["must use npx", "no downtime"]);

  assert.equal(board.status, "planning");
  assert.deepEqual(board.conflicts, []);
});

test("buildBoard flags checkmate when constraints contradict", () => {
  const board = buildBoard("Ship a thing", [
    "must use external API",
    "cannot use external API"
  ]);

  assert.equal(board.status, "checkmate");
  assert.equal(board.conflicts.length, 1);
  assert.equal(board.conflicts[0].conflict_type, "constraint");
  assert.equal(board.conflicts[0].severity, "critical");
  assert.equal(board.conflicts[0].blocking, true);
  assert.match(board.conflicts[0].summary, /Hard constraints contradict/);
  assert.ok(board.conflicts[0].agents_involved.includes("rook_logic"));
});

test("findConstraintContradiction returns null on empty list", () => {
  assert.equal(findConstraintContradiction([]), null);
});

test("findConstraintContradiction returns null on single constraint", () => {
  assert.equal(findConstraintContradiction(["must use API"]), null);
});

test("findConstraintContradiction is case-insensitive", () => {
  const result = findConstraintContradiction(["Must Use API", "CANNOT use api"]);

  assert.ok(result);
  assert.match(result, /contradict/);
});

test("findConstraintContradiction strips filler words", () => {
  const result = findConstraintContradiction([
    "must use the API",
    "cannot use the API"
  ]);

  assert.ok(result);
  assert.match(result, /contradict/);
});

test("findConstraintContradiction ignores differing normalized actions", () => {
  assert.equal(
    findConstraintContradiction(["must launch Friday", "cannot launch Monday"]),
    null
  );
});

test("formatText prepends CHECKMATE block when status is checkmate", () => {
  const board = buildBoard("Ship a thing", [
    "must use external API",
    "cannot use external API"
  ]);
  const text = formatText(board);

  assert.match(text, /CHECKMATE:/);
  assert.match(text, /relax the objective/);
});
