"""Conflict resolution for CheckMate."""

from __future__ import annotations

from .board import BoardState
from .models import ConflictOutcome, ConflictType, RuntimeStatus, Severity


class ConflictResolver:
    """Applies authority rules to unresolved conflicts."""

    def resolve(self, board: BoardState) -> list[ConflictOutcome]:
        outcomes: list[ConflictOutcome] = []
        for conflict in board.conflicts:
            if conflict.resolved:
                continue
            outcome = self._decide(conflict.conflict_type, conflict.severity, conflict.blocking)
            conflict.resolved = True
            conflict.resolution_outcome = outcome
            outcomes.append(outcome)

        if ConflictOutcome.DECLARE_CHECKMATE in outcomes:
            board.status = RuntimeStatus.CHECKMATE
        elif ConflictOutcome.DECLARE_CHECK in outcomes:
            board.status = RuntimeStatus.CHECK
        return outcomes

    def _decide(
        self,
        conflict_type: ConflictType,
        severity: Severity,
        blocking: bool,
    ) -> ConflictOutcome:
        if not blocking:
            return ConflictOutcome.REVISE_PLAN
        if conflict_type in {ConflictType.GOAL, ConflictType.CONSTRAINT} and severity == Severity.CRITICAL:
            return ConflictOutcome.DECLARE_CHECKMATE
        if severity in {Severity.HIGH, Severity.CRITICAL}:
            return ConflictOutcome.DECLARE_CHECK
        if conflict_type == ConflictType.EVIDENCE:
            return ConflictOutcome.RUN_EXPERIMENT
        if conflict_type == ConflictType.EXECUTION:
            return ConflictOutcome.REVISE_PLAN
        if conflict_type == ConflictType.INTERPRETATION:
            return ConflictOutcome.ESCALATE_TO_KING
        return ConflictOutcome.REVISE_PLAN
