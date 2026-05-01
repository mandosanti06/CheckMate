---
name: checkmate-agent-system
description: Use this skill to structure complex planning, implementation, architecture, research, review, or recovery work with the CheckMate chess-piece agent system: King governance, Queen orchestration, Rook validation, Bishop analysis, Knight exploration, Pawn execution, check/checkmate states, conflict resolution, and pawn promotion.
---

# CheckMate Agent System

Use CheckMate to turn ambiguous work into governed, constraint-aware execution.
Treat chess pieces as reasoning primitives with authority boundaries, not
personalities.

## Core Contract

- King defines objective, constraints, success criteria, final approval, and check/checkmate. The King does not plan or execute.
- Queen decomposes, assigns, sequences, and synthesizes. The Queen must not bypass Rook vetoes or replace every other piece.
- Rooks validate hard structure: logic, dependencies, resources, tools, time, and external limits. Rooks may veto invalid execution.
- Bishops infer meaning, causes, patterns, consequences, and tradeoffs. Bishops recommend but do not approve.
- Knights generate alternatives, assumption challenges, unusual paths, and recovery options. Knights may interrupt but not override King or Rooks.
- Pawns execute atomic work and report observed evidence. Pawns are narrow, not less intelligent.

## Default Workflow

1. King: restate the objective, hard constraints, soft constraints, and success criteria.
2. Queen: decompose the goal into workstreams and assign piece responsibilities.
3. Bishops: analyze implications, risks, patterns, and longer-term consequences.
4. Rooks: validate feasibility and identify hard blockers or vetoes.
5. Knights: propose alternatives, shortcuts, fallback paths, and experiments.
6. Queen: synthesize one executable plan with dependencies and owners.
7. King: approve, reject, request revision, declare check, or declare checkmate.
8. Pawns: execute the smallest concrete tasks and report evidence.
9. Loop when new evidence, blockers, or changed constraints appear.

## Output Shape

For most tasks, produce a concise CheckMate brief:

```text
King: objective, constraints, success criteria
Bishops: implications and risks
Rooks: feasibility result and vetoes if any
Knights: alternatives and recovery paths
Queen: executable sequence
Pawns: atomic next actions and evidence to collect
Decision: approved, revise, check, or checkmate
```

For implementation work, convert the Pawn section into actual file edits,
commands, tests, and verification steps. Keep role labels in the reasoning
artifact; do not over-label ordinary user-facing progress updates.

## Check And Checkmate

Declare `check` when the goal is threatened but recovery may be possible:
deadline risk, resource shortage, contradictory requirements, execution failure,
or missing information. Pause execution, ask Rooks for feasibility review, ask
Knights for alternatives, and return to the King if the goal must change.

Declare `checkmate` when no valid plan satisfies the current goal and hard
constraints. Stop planning and ask the King to relax the goal, relax constraints,
or redefine success.

## Conflict Rules

Resolve by authority:

1. King: objective and final approval
2. Rook: hard constraints and feasibility veto
3. Queen: plan synthesis and sequencing
4. Bishop: interpretation and forecasting
5. Knight: alternatives and edge cases
6. Pawn: ground-truth execution reports

Exception: Pawn reports override assumptions when they contain real execution
results.

## Promotion

Promote a Pawn when repeated atomic work starts requiring durable judgment:
Research Pawn to Bishop for strategic insight, Coding Pawn to Rook for
architecture enforcement, QA Pawn to Knight for unusual edge cases, or Operations
Pawn to Queen-lite for recurring coordination.

## Bundled Resources

- Read `references/piece-system.md` when designing a CheckMate runtime, prompt set, or agent topology.
- Read `references/schemas.md` when needing structured agent, message, board, conflict, or tool-access JSON.
- Run `scripts/checkmate_plan.py` when a deterministic text or JSON planning skeleton is useful.

Example:

```bash
python3 scripts/checkmate_plan.py \
  --goal "Build a migration plan" \
  --constraint "must preserve uptime" \
  --constraint "deadline is 2 weeks" \
  --format json
```

