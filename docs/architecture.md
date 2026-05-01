# CheckMate Architecture

CheckMate models each chess piece as a different reasoning primitive. The
runtime is not a collection of unconstrained chat agents. It is a governed
planning system with explicit authority boundaries.

## Core Components

```text
CheckMate System
├── Board State
├── Piece Agents
├── Message Bus
├── Tool Registry
├── Conflict Resolver
├── Memory Layer
└── Execution Engine
```

## Authority Model

| Piece | Runtime role | Authority |
| --- | --- | --- |
| King | Governance | Sets objective, constraints, approval, check/checkmate |
| Queen | Orchestration | Decomposes goals, assigns agents, synthesizes plans |
| Rooks | Validation | Validate rules, dependencies, resources, feasibility |
| Bishops | Analysis | Interpret meaning, risks, patterns, consequences |
| Knights | Exploration | Generate alternatives, workarounds, recovery paths |
| Pawns | Execution | Complete atomic work and report observed results |

## Communication Topology

- King messages flow to the Queen.
- Queen can assign and coordinate all pieces.
- Bishops, Rooks, and Knights can communicate horizontally with their matching
  piece type.
- Knights can interrupt any agent with alternatives or recovery paths.
- Pawns report to the Queen and cannot freely talk to other Pawns.
- Rooks can send veto notices for hard feasibility failures.

## Check and Checkmate

`check` means the goal is threatened but recovery may still be possible.
Execution pauses, the Queen is notified, Rooks review feasibility, and Knights
search for alternatives.

`checkmate` means no valid plan satisfies the current goal and constraints.
Planning stops. The King records that the objective, constraints, or success
criteria must be changed.

## Promotion

Pawns are narrow rather than less capable. A Pawn can request promotion after
repeated success, accumulated context, recurring pattern detection, or work
that starts requiring judgment instead of simple execution.
