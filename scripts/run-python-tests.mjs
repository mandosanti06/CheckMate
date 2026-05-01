import { spawnSync } from "node:child_process";

const attempts = [
  { command: "python3", args: ["-m", "unittest", "discover", "-s", "tests"] },
  { command: "python", args: ["-m", "unittest", "discover", "-s", "tests"] },
  { command: "py", args: ["-3", "-m", "unittest", "discover", "-s", "tests"] }
];

let lastError = null;

for (const attempt of attempts) {
  const result = spawnSync(attempt.command, attempt.args, { stdio: "inherit" });
  if (result.error && result.error.code === "ENOENT") {
    lastError = result.error;
    continue;
  }
  if (result.error) {
    throw result.error;
  }
  process.exit(result.status ?? 1);
}

console.error("Could not find a Python executable. Tried python3, python, and py -3.");
if (lastError) {
  console.error(lastError.message);
}
process.exit(1);
