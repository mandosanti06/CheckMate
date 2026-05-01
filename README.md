# CheckMate Agent System

[![Status: alpha](https://img.shields.io/badge/status-alpha-orange)](#status--scope)
[![npm version](https://img.shields.io/npm/v/checkmate-agent-system?color=cb3837)](https://www.npmjs.com/package/checkmate-agent-system)
[![npm downloads](https://img.shields.io/npm/dm/checkmate-agent-system?color=blue)](https://www.npmjs.com/package/checkmate-agent-system)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D18-339933?logo=node.js&logoColor=white)](package.json)
[![Skills](https://img.shields.io/badge/Codex%20%2B%20Claude-skills-7c3aed)](skills/checkmate-agent-system/SKILL.md)

**Chess-governed multi-agent planning for Claude Code, Codex, npm/npx, and Python.**

CheckMate is an open source multi-agent orchestration framework and prompt-engineering system built around chess-piece roles. It ships as a Claude Code skill, Codex skill, npm CLI, npx package, and Python runtime for structured, constraint-based planning.

_Don't let the Queen become everything. Make the system think with constraints._

[Quick Start](#quick-start) • [npx CLI](#npx-cli) • [Skill Package](#skill-package) • [Runtime](#python-runtime) • [Architecture](docs/architecture.md) • [npx Reference](docs/NPX.md)

---

## Status & Scope

CheckMate is alpha (0.1.0). Read this before you wire it into anything.

- The Python runtime is a deterministic governance scaffold. It does not call an LLM. Bring your own model integration in your own agent loop.
- The npm CLI emits a planning skeleton (text or JSON) with a naive hard-constraint contradiction heuristic. It is not a full runtime; the Python package is where the conflict resolver and message-bus topology live.
- The skill bundle is a prompt-engineering frame meant to be loaded into Claude Code or Codex sessions. It shapes how a model reasons; it is not itself a model.
- "Agent" here means a typed role with permissions and message routing, not an LLM-backed actor.

---

## Quick Start

### Step 1: Run with npx

```bash
npx checkmate-agent-system@latest plan \
  --goal "Build a migration plan" \
  --constraint "must preserve uptime" \
  --constraint "deadline is 2 weeks"
```

JSON output:

```bash
npx checkmate-agent-system@latest plan \
  --goal "Build a migration plan" \
  --constraint "must preserve uptime" \
  --format json
```

### Step 2: Install the skill

Codex:

```bash
npx checkmate-agent-system@latest install codex
```

Claude Code user scope:

```bash
npx checkmate-agent-system@latest install claude
```

Claude Code project scope:

```bash
npx checkmate-agent-system@latest install claude-project
```

### Step 3: Use it in-session

In Claude Code or Codex, mention CheckMate or the chess pieces in your prompt — the skill auto-loads on relevance based on its `SKILL.md` description. There is no `$name` invocation syntax.

```text
Use CheckMate to plan this feature with King, Queen, Rooks, Bishops, Knights, and Pawns.
```

That gives you a governed loop:

```text
King -> Queen -> Bishops -> Rooks -> Knights -> Queen -> King -> Pawns
```

---

## What Is CheckMate?

CheckMate is a general-purpose agent system where each chess piece is a
constraint-based reasoning primitive:

| Piece | Runtime role | Authority |
| --- | --- | --- |
| King | Governance | Objective, constraints, success criteria, final approval |
| Queen | Orchestration | Decomposition, assignment, synthesis, sequencing |
| Rooks | Validation | Logic, dependencies, resources, timeline, vetoes |
| Bishops | Analysis | Causality, patterns, implications, tradeoffs |
| Knights | Exploration | Alternatives, workarounds, recovery paths |
| Pawns | Execution | Atomic tasks, observations, evidence reports |

The core idea:

- **who thinks**
- **how they think**
- **what they are allowed to influence**

## npx CLI

CheckMate exposes a dependency-free Node CLI.

```bash
# One-shot planning
npx checkmate-agent-system@latest plan --goal "Design an auth system" -c "must support SSO"

# Install portable skill bundle
npx checkmate-agent-system@latest install codex
npx checkmate-agent-system@latest install claude
npx checkmate-agent-system@latest install claude-project

# Replace existing skill install
npx checkmate-agent-system@latest install codex --force

# Inspect package paths
npx checkmate-agent-system@latest doctor
npx checkmate-agent-system@latest skill-path
npx checkmate-agent-system@latest zip-path
```

Install globally if you prefer a persistent command:

```bash
npm i -g checkmate-agent-system@latest
checkmate plan --goal "Ship the release" -c "no downtime"
```

### CLI Commands vs Skill Usage

| Feature | Terminal CLI | In-session skill | Notes |
| --- | --- | --- | --- |
| Plan skeleton | `checkmate plan ...` | mention CheckMate in prompt | CLI emits text or JSON; skill guides the agent's reasoning. |
| Codex install | `checkmate install codex` | — | Copies the skill into `${CODEX_HOME:-~/.codex}/skills`. |
| Claude install | `checkmate install claude` | — | Copies the skill into `~/.claude/skills`. |
| Project install | `checkmate install claude-project` | — | Copies the skill into `.claude/skills` for the current project. |
| Diagnostics | `checkmate doctor` | — | Checks bundled skill and default target paths. |
| Runtime execution | Python API | — | Use the Python runtime for programmatic board/agent execution. |

The CLI emits a planning skeleton and catches simple direct contradictions such as `must use external API` plus `cannot use external API`. The full conflict resolver and message-bus runtime live in Python.

## Skill Package

The portable skill lives here:

```text
skills/checkmate-agent-system/
  SKILL.md
  agents/openai.yaml
  references/piece-system.md
  references/schemas.md
  scripts/checkmate_plan.py
```

For Claude.ai custom skill upload, use:

```text
dist/checkmate-agent-system-skill.zip
```

The ZIP root contains `checkmate-agent-system/`, so it is ready for upload/import.

Manual install is still supported:

```bash
cp -R skills/checkmate-agent-system "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/checkmate-agent-system ~/.claude/skills/
mkdir -p .claude/skills && cp -R skills/checkmate-agent-system .claude/skills/
```

## Python Runtime

The repo also includes a Python runtime that models the board, pieces, message
bus, tool permissions, conflict resolver, memory layer, and execution engine.

```bash
python3 examples/basic_runtime.py
python3 -m unittest discover -s tests
```

```python
from checkmate import ExecutionEngine

engine = ExecutionEngine.default()
board = engine.run(
    goal="Build a project plan for an API migration",
    constraints=[
        "must preserve uptime",
        "deadline is 2 weeks",
        "use existing team capacity",
    ],
)

print(board.status)
print(board.current_plan)
```

## Features

- **Governance-first planning**: King owns objective, constraints, approval, check, and checkmate.
- **Explicit orchestration**: Queen decomposes and synthesizes without bypassing validators.
- **Rook validation pattern** (logic + resources, currently keyword-heuristic).
- **Strategic analysis**: Bishops surface causal effects, patterns, and tradeoffs.
- **Nonlinear recovery**: Knights challenge assumptions and generate fallback paths.
- **Pawn role for atomic execution and evidence reporting** (you wire the actual execution to your tools).
- **Portable skills**: One skill folder works for Codex and Claude-style skill imports.
- **npx-ready CLI**: Install skills and emit planning skeletons from any terminal.

## Check And Checkmate

`check` means the goal is threatened but recovery may still be possible:
deadline risk, resource shortage, missing information, contradictory
requirements, or execution failure.

`checkmate` means no valid plan satisfies the current goal and hard constraints.
The system must stop and ask the King to relax the objective, relax constraints,
or redefine success.

## Requirements

| Surface | Requirement |
| --- | --- |
| npx CLI | Node.js 18+ |
| Codex skill install | Codex with a skills folder, usually `~/.codex/skills` |
| Claude Code skill install | Claude Code with `~/.claude/skills` or project `.claude/skills` |
| Python runtime | Python 3.9+ |

## Development

```bash
# Run Node and Python tests
npm run check

# Try the CLI locally
node bin/checkmate.js plan --goal "Package CheckMate" -c "must work with npx"
node bin/checkmate.js doctor

# Inspect npm package contents before publishing
npm pack --dry-run
```

Publish when ready:

```bash
npm login
npm publish
```

> Package note: the project is branded **CheckMate Agent System** and the npm
> package is `checkmate-agent-system`.

## Documentation

- [Architecture](docs/architecture.md)
- [npx Reference](docs/NPX.md)
- [Skill entrypoint](skills/checkmate-agent-system/SKILL.md)
- [Piece system reference](skills/checkmate-agent-system/references/piece-system.md)
- [Schemas reference](skills/checkmate-agent-system/references/schemas.md)

## License

MIT

---

<div align="center">

**Governance, synthesis, validation, analysis, exploration, execution.**

_A chess side for thinking._

</div>
