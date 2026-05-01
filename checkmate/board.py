"""Shared board state for the CheckMate runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .models import (
    Conflict,
    ConflictOutcome,
    Constraint,
    Decision,
    Risk,
    RuntimeStatus,
    Task,
    TaskStatus,
    to_plain_data,
)


@dataclass
class BoardState:
    goal: str
    constraints: list[Constraint] = field(default_factory=list)
    active_agents: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    risks: list[Risk] = field(default_factory=list)
    conflicts: list[Conflict] = field(default_factory=list)
    status: RuntimeStatus = RuntimeStatus.IDLE
    context: dict[str, Any] = field(default_factory=dict)
    current_plan: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        self.constraints = [
            Constraint.from_value(constraint) for constraint in self.constraints
        ]

    def register_agent(self, agent_id: str) -> None:
        if agent_id not in self.active_agents:
            self.active_agents.append(agent_id)

    def add_task(self, task: Task) -> None:
        if not any(existing.id == task.id for existing in self.tasks):
            self.tasks.append(task)

    def get_task(self, task_id: str) -> Optional[Task]:
        return next((task for task in self.tasks if task.id == task_id), None)

    def tasks_for(self, agent_id: str) -> list[Task]:
        return [task for task in self.tasks if task.assigned_to == agent_id]

    def mark_task(
        self, task_id: str, status: TaskStatus, evidence: Optional[list[str]] = None
    ) -> None:
        task = self.get_task(task_id)
        if task is None:
            return
        task.status = status
        if evidence:
            task.evidence.extend(evidence)

    def add_decision(self, decision: Decision) -> None:
        if not any(existing.id == decision.id for existing in self.decisions):
            self.decisions.append(decision)

    def add_risk(self, risk: Risk) -> None:
        if not any(existing.summary == risk.summary for existing in self.risks):
            self.risks.append(risk)

    def add_conflict(self, conflict: Conflict) -> None:
        if not any(existing.summary == conflict.summary for existing in self.conflicts):
            self.conflicts.append(conflict)

    def has_blocking_conflicts(self) -> bool:
        return any(conflict.blocking and not conflict.resolved for conflict in self.conflicts)

    def has_veto(self) -> bool:
        return any(
            conflict.resolution_outcome
            in {ConflictOutcome.DECLARE_CHECK, ConflictOutcome.DECLARE_CHECKMATE}
            for conflict in self.conflicts
        )

    def hard_constraints(self) -> list[Constraint]:
        return [constraint for constraint in self.constraints if constraint.hard]

    def apply_updates(self, updates: dict[str, Any]) -> None:
        """Apply a structured patch emitted by an agent."""

        for task in updates.get("tasks_to_add", []):
            self.add_task(task)
        for task_id, status in updates.get("task_statuses", {}).items():
            evidence = updates.get("task_evidence", {}).get(task_id)
            self.mark_task(task_id, status, evidence)
        for risk in updates.get("risks_to_add", []):
            self.add_risk(risk)
        for conflict in updates.get("conflicts_to_add", []):
            self.add_conflict(conflict)
        for decision in updates.get("decisions_to_add", []):
            self.add_decision(decision)
        if "status" in updates:
            self.status = RuntimeStatus(updates["status"])
        if "current_plan" in updates:
            self.current_plan = updates["current_plan"]
        if "context" in updates:
            self.context.update(updates["context"])

    def to_dict(self) -> dict[str, Any]:
        return to_plain_data(self)
