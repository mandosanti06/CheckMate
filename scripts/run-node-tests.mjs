import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const testsDir = path.resolve("tests", "node");
const testFiles = fs
  .readdirSync(testsDir)
  .filter((name) => name.endsWith(".test.js"))
  .sort()
  .map((name) => path.join(testsDir, name));

if (testFiles.length === 0) {
  console.error(`No Node test files found in ${testsDir}`);
  process.exit(1);
}

const result = spawnSync(process.execPath, ["--test", ...testFiles], {
  stdio: "inherit"
});

if (result.error) {
  throw result.error;
}

process.exit(result.status ?? 1);
