#!/usr/bin/env python3
"""Emit a deterministic CheckMate planning skeleton."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from typing import Any


PIECES = {
    "king": "Define objective, constraints, success criteria, and final decision.",
    "queen": "Decompose, assign, sequence, and synthesize the plan.",
    "bishop_causal": "Analyze causes, dependencies over time, and second-order effects.",
    "bishop_pattern": "Identify reusable patterns, analogies, and strategic tradeoffs.",
    "rook_logic": "Validate rules, contradictions, dependencies, and acceptance criteria.",
    "rook_resource": "Validate time, resources, tools, capacity, and external limits.",
    "knight_creative": "Generate alternatives, simplifications, and unexpected paths.",
    "knight_recovery": "Generate fallback paths, workarounds, and recovery experiments.",
    "pawn_research": "Gather raw information and sources.",
    "pawn_writing": "Draft or rewrite text.",
    "pawn_coding": "Implement code changes.",
    "pawn_design": "Shape UX, wireframes, or visual hierarchy.",
    "pawn_data": "Handle tables, schemas, metrics, or calculations.",
    "pawn_communication": "Prepare stakeholder messages.",
    "pawn_operations": "Run checklists, schedules, or deployment steps.",
    "pawn_qa": "Test, review, and report defects.",
}


def normalize_action(text: str) -> str:
    result = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    result = re.sub(r"\b(must|should|required|requires|require|cannot|can not|use|using)\b", " ", result)
    result = re.sub(r"\b(no|not|the|a|an|to|on|with|without)\b", " ", result)
    result = result.replace("apis", "api")
    return " ".join(result.split())


def find_constraint_contradiction(constraints: list[str]) -> str | None:
    positive: dict[str, str] = {}
    negative: dict[str, str] = {}

    for raw in constraints:
        text = raw.lower()
        has_negative = re.search(r"\b(must not|cannot|can not|no)\b", text)
        has_positive = re.search(r"\b(must|requires|required)\b", text)

        if has_positive and not has_negative:
            positive[normalize_action(text)] = raw
        if has_negative:
            negative[normalize_action(text)] = raw

    for action, pos_text in positive.items():
        if action and action in negative:
            return (
                "Hard constraints contradict each other: "
                f"'{pos_text}' conflicts with '{negative[action]}'."
            )
    return None


def build_board(goal: str, constraints: list[str]) -> dict[str, Any]:
    contradiction = find_constraint_contradiction(constraints)
    conflicts = []
    if contradiction:
        conflicts.append(
            {
                "conflict_type": "constraint",
                "severity": "critical",
                "blocking": True,
                "summary": contradiction,
                "agents_involved": ["rook_logic", "king", "queen"],
            }
        )

    return {
        "goal": goal,
        "constraints": [{"description": item, "hard": True} for item in constraints],
        "status": "checkmate" if contradiction else "planning",
        "active_agents": list(PIECES.keys()),
        "tasks": [
            {
                "id": "king_goal",
                "assigned_to": "king",
                "title": "Define governance frame",
                "expected_output": "Objective, constraints, success criteria, decision criteria.",
            },
            {
                "id": "queen_decompose",
                "assigned_to": "queen",
                "title": "Decompose objective",
                "expected_output": "Workstreams, owners, dependencies, and approval request.",
            },
            {
                "id": "bishops_analyze",
                "assigned_to": "bishop_causal,bishop_pattern",
                "title": "Analyze meaning and consequences",
                "expected_output": "Risks, forecasts, patterns, tradeoffs, recommendations.",
            },
            {
                "id": "rooks_validate",
                "assigned_to": "rook_logic,rook_resource",
                "title": "Validate feasibility",
                "expected_output": "Valid, invalid, blocked, risk, or veto.",
            },
            {
                "id": "knights_explore",
                "assigned_to": "knight_creative,knight_recovery",
                "title": "Explore alternatives",
                "expected_output": "Alternatives, workarounds, assumption challenges, recovery paths.",
            },
            {
                "id": "pawns_execute",
                "assigned_to": "pawns",
                "title": "Execute atomic tasks",
                "expected_output": "Evidence-backed execution reports and blockers.",
            },
        ],
        "decisions": [],
        "risks": [],
        "conflicts": conflicts,
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "runtime": "checkmate-agent-system skill",
        },
    }


def format_text(board: dict[str, Any]) -> str:
    constraints = board["constraints"] or [{"description": "none specified"}]
    lines = [
        "CheckMate Brief",
        "",
        f"King: {board['goal']}",
        "Constraints:",
    ]
    lines.extend(f"- {item['description']}" for item in constraints)
    lines.extend(
        [
            "",
            "Bishops: analyze causal implications, patterns, risks, and tradeoffs.",
            "Rooks: validate hard constraints, dependencies, resources, and timeline.",
            "Knights: propose alternatives, assumption challenges, and recovery paths.",
            "Queen: synthesize a dependency-ordered plan and request approval.",
            "Pawns: execute the smallest concrete tasks and report evidence.",
            "Decision: pending King approval.",
            "",
            "Suggested tasks:",
        ]
    )
    lines.extend(
        f"- {task['id']} ({task['assigned_to']}): {task['title']}"
        for task in board["tasks"]
    )
    if board["status"] == "checkmate" and board["conflicts"]:
        lines = [
            f"CHECKMATE: {board['conflicts'][0]['summary']}",
            "The King must relax the objective, relax constraints, or redefine success.",
            "",
            *lines,
        ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goal", required=True, help="Current objective.")
    parser.add_argument(
        "--constraint",
        action="append",
        default=[],
        help="Constraint to include. Repeat for multiple constraints.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    args = parser.parse_args()

    board = build_board(args.goal, args.constraint)
    if args.format == "json":
        print(json.dumps(board, indent=2, sort_keys=True))
    else:
        print(format_text(board))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
