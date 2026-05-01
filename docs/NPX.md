# npx Usage

CheckMate ships a dependency-free Node CLI for fast use through npm or npx.

## One-shot Planning

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

## Install The Skill

Codex user-scope skill:

```bash
npx checkmate-agent-system@latest install codex
```

Claude Code user-scope skill:

```bash
npx checkmate-agent-system@latest install claude
```

Claude Code project-scope skill:

```bash
npx checkmate-agent-system@latest install claude-project
```

Replace an existing install:

```bash
npx checkmate-agent-system@latest install codex --force
```

Use a custom skills root:

```bash
npx checkmate-agent-system@latest install codex --path /path/to/skills
```

## Diagnostics

```bash
npx checkmate-agent-system@latest doctor
npx checkmate-agent-system@latest skill-path
npx checkmate-agent-system@latest zip-path
```

