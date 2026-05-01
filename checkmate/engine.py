"""Execution engine for the CheckMate runtime."""

from __future__ import annotations

from typing import Iterable, Optional, Union

from .agents import PieceAgent, default_agents
from .board import BoardState
from .conflicts import ConflictResolver
from .messages import MessageBus, TopologyViolation
from .models import (
    AgentStatus,
    Conflict,
    ConflictType,
    Constraint,
    RuntimeStatus,
    Severity,
    TaskStatus,
)
from .tools import ToolRegistry, default_tool_registry


class ExecutionEngine:
    """Controls turn order and applies agent outputs to the board."""

    def __init__(
        self,
        agents: Iterable[PieceAgent],
        tool_registry: Optional[ToolRegistry] = None,
        message_bus: Optional[MessageBus] = None,
        conflict_resolver: Optional[ConflictResolver] = None,
    ) -> None:
        self.tool_registry = tool_registry or default_tool_registry()
        self.agents = {agent.agent_id: agent for agent in agents}
        self.message_bus = message_bus or MessageBus()
        self.conflict_resolver = conflict_resolver or ConflictResolver()
        for agent in self.agents.values():
            self.message_bus.register_agent(agent.agent_id, agent.piece)

    @classmethod
    def default(cls) -> "ExecutionEngine":
        registry = default_tool_registry()
        return cls(default_agents(registry), tool_registry=registry)

    def run(
        self,
        goal: str,
        constraints: Optional[list[Union[str, dict, Constraint]]] = None,
        context: Optional[dict] = None,
    ) -> BoardState:
        board = BoardState(goal=goal, constraints=constraints or [], context=context or {})
        return self.run_board(board)

    def run_board(self, board: BoardState) -> BoardState:
        board.status = RuntimeStatus.PLANNING

        self._run_agent(board, "king")
        self._run_agent(board, "queen", {"phase": "decompose"})

        self._run_agent(board, "bishop_causal")
        self._run_agent(board, "bishop_pattern")

        board.status = RuntimeStatus.VALIDATING
        self._run_agent(board, "rook_logic")
        self._run_agent(board, "rook_resource")
        self.conflict_resolver.resolve(board)

        if board.status == RuntimeStatus.CHECKMATE:
            self._run_agent(board, "king")
            return board

        self._run_agent(board, "knight_creative")
        self._run_agent(board, "knight_recovery")

        self._run_agent(board, "queen", {"phase": "synthesize"})
        self.conflict_resolver.resolve(board)

        self._run_agent(board, "king")
        if board.status in {RuntimeStatus.CHECK, RuntimeStatus.CHECKMATE}:
            return board

        if board.status == RuntimeStatus.EXECUTING:
            self._execute_pawns(board)

        if not board.has_blocking_conflicts():
            board.status = RuntimeStatus.COMPLETE
        return board

    def _execute_pawns(self, board: BoardState) -> None:
        for pawn_id in [
            "pawn_research",
            "pawn_writing",
            "pawn_coding",
            "pawn_design",
            "pawn_data",
            "pawn_communication",
            "pawn_operations",
            "pawn_qa",
        ]:
            self._run_agent(board, pawn_id)
        if any(task.status == TaskStatus.BLOCKED for task in board.tasks):
            board.status = RuntimeStatus.CHECK

    def _run_agent(
        self,
        board: BoardState,
        agent_id: str,
        assigned_task: Optional[dict] = None,
    ) -> None:
        agent = self.agents[agent_id]
        board.register_agent(agent_id)
        messages = self.message_bus.drain_for(agent_id)
        result = agent.run(board, messages, assigned_task=assigned_task)
        board.apply_updates(result.updates)
        self._record_agent_output(board, result.output, agent_id)
        try:
            self.message_bus.submit_many(result.messages)
        except TopologyViolation as exc:
            board.add_conflict(
                Conflict(
                    conflict_type=ConflictType.EXECUTION,
                    agents_involved=[agent_id],
                    severity=Severity.HIGH,
                    blocking=True,
                    summary=str(exc),
                )
            )

        if result.output.status == AgentStatus.CONFLICT and result.status == "blocked":
            board.status = RuntimeStatus.CHECK

    def _record_agent_output(
        self,
        board: BoardState,
        output,
        agent_id: str,
    ) -> None:
        agent_outputs = dict(board.context.get("agent_outputs", {}))
        agent_outputs[agent_id] = {
            "status": output.status.value,
            "summary": output.summary,
            "findings": output.findings,
            "recommendations": output.recommendations,
            "risks": output.risks,
            "proposed_actions": output.proposed_actions,
            "confidence": output.confidence,
        }
        board.context["agent_outputs"] = agent_outputs
