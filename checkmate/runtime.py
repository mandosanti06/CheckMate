"""Convenience entry points."""

from __future__ import annotations

from typing import Optional, Union

from .board import BoardState
from .engine import ExecutionEngine
from .models import Constraint


def run_checkmate(
    goal: str,
    constraints: Optional[list[Union[str, dict, Constraint]]] = None,
    context: Optional[dict] = None,
) -> BoardState:
    return ExecutionEngine.default().run(goal, constraints=constraints, context=context)
