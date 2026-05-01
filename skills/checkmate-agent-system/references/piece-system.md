# CheckMate Piece System

Use this reference when implementing or adapting the CheckMate architecture.

## Pieces

| Piece | Agent count | Reasoning mode | Responsibility |
| --- | ---: | --- | --- |
| King | 1 | evaluative | Objective, constraints, success criteria, approval |
| Queen | 1 | executive | Decomposition, orchestration, synthesis |
| Rooks | 2 | linear | Logic validation and resource validation |
| Bishops | 2 | diagonal | Causal reasoning and pattern recognition |
| Knights | 2 | nonlinear | Creative alternatives and recovery paths |
| Pawns | 8 | atomic | Research, writing, coding, design, data, communication, operations, QA |

## Specializations

- King: governance agent.
- Queen: orchestration agent.
- Rook 1: logic rook for rules, contradictions, dependencies, acceptance criteria.
- Rook 2: resource rook for time, budget, tools, people, capacity, external limitations.
- Bishop 1: causal bishop for root causes, second-order effects, risk propagation.
- Bishop 2: pattern bishop for trends, analogies, reusable patterns, historical comparison.
- Knight 1: creative knight for novel approaches and simplification.
- Knight 2: recovery knight for blockers, fallback paths, and emergency replanning.
- Pawns: narrow executors/observers for research, writing, coding, design, data,
  communication, operations, and QA.

## Communication Topology

- Vertical control: King to Queen to other pieces.
- Horizontal alignment: Bishop to Bishop, Rook to Rook, Knight to Knight.
- Pawns report upward to Queen and should not freely coordinate with each other.
- Knights may interrupt any piece with alternatives or recovery proposals.
- Rooks may veto execution when hard constraints fail.
- Agents should communicate by structured messages, not free-form chat.

## Tool Access

- King: read global state, evaluate/approve/reject plans, set objectives and constraints, trigger replanning.
- Queen: assign tasks, merge outputs, create and sequence plans, request reviews, submit for approval.
- Rooks: validate constraints, check dependencies/resources, verify timelines, audit plans, block invalid actions.
- Bishops: analyze context, detect patterns, forecast outcomes, identify risks, compare options, explain tradeoffs.
- Knights: generate alternatives, challenge assumptions, find workarounds, simulate unusual paths, recover from blockers, stress-test plans.
- Pawns: execute atomic tasks, collect data, summarize results, report blockers, request promotion.

## Planning Cycle

1. King defines goal.
2. Queen decomposes goal.
3. Bishops analyze meaning and risk.
4. Rooks validate feasibility.
5. Knights generate alternatives.
6. Queen synthesizes plan.
7. King approves or blocks.
8. Pawns execute.
9. System evaluates, then loops.

## Failure Modes

- Vague King: unstable goals and drifting success criteria.
- Overused Queen: monolithic planning that ignores distributed reasoning.
- Bypassed Rooks: fast answers with weak reliability.
- Ignored Knights: stale plans with poor recovery options.
- Over-chatty Pawns: noisy execution and unclear evidence ownership.

