"""Permissioned tool registry for piece agents."""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import Piece


class ToolPermissionError(PermissionError):
    """Raised when a piece attempts to use a tool outside its authority."""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    allowed_pieces: set[Piece]
    requires_approval: bool = False
    category: str = "general"
    description: str = ""


@dataclass
class ToolRegistry:
    tools: dict[str, ToolSpec] = field(default_factory=dict)

    def register(self, spec: ToolSpec) -> None:
        self.tools[spec.name] = spec

    def allowed_tools_for(self, piece: Piece) -> list[str]:
        return sorted(
            name for name, spec in self.tools.items() if piece in spec.allowed_pieces
        )

    def assert_allowed(self, piece: Piece, tool_name: str) -> ToolSpec:
        spec = self.tools.get(tool_name)
        if spec is None:
            raise ToolPermissionError(f"Unknown tool: {tool_name}")
        if piece not in spec.allowed_pieces:
            raise ToolPermissionError(
                f"{piece.value} cannot use {tool_name}; allowed pieces are "
                f"{', '.join(sorted(item.value for item in spec.allowed_pieces))}"
            )
        return spec


def default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    def add(
        name: str,
        pieces: set[Piece],
        category: str,
        requires_approval: bool = False,
    ) -> None:
        registry.register(
            ToolSpec(
                name=name,
                allowed_pieces=pieces,
                category=category,
                requires_approval=requires_approval,
            )
        )

    add("read_global_state", {Piece.KING, Piece.QUEEN}, "governance")
    add("evaluate_plan", {Piece.KING}, "governance")
    add("approve_plan", {Piece.KING}, "governance")
    add("reject_plan", {Piece.KING}, "governance")
    add("set_objective", {Piece.KING}, "governance")
    add("set_constraints", {Piece.KING}, "governance")
    add("trigger_replan", {Piece.KING}, "governance")

    add("assign_task", {Piece.QUEEN}, "orchestration")
    add("merge_outputs", {Piece.QUEEN}, "orchestration")
    add("create_plan", {Piece.QUEEN}, "orchestration")
    add("sequence_tasks", {Piece.QUEEN}, "orchestration")
    add("request_agent_review", {Piece.QUEEN}, "orchestration")
    add("submit_for_approval", {Piece.QUEEN}, "orchestration")

    add("validate_constraints", {Piece.ROOK}, "validation")
    add("check_dependencies", {Piece.ROOK}, "validation")
    add("check_resources", {Piece.ROOK}, "validation")
    add("verify_timeline", {Piece.ROOK}, "validation")
    add("audit_plan", {Piece.ROOK}, "validation")
    add("block_invalid_action", {Piece.ROOK}, "validation")

    add("analyze_context", {Piece.BISHOP}, "analysis")
    add("detect_patterns", {Piece.BISHOP}, "analysis")
    add("forecast_outcomes", {Piece.BISHOP}, "analysis")
    add("identify_risks", {Piece.BISHOP}, "analysis")
    add("compare_options", {Piece.BISHOP}, "analysis")
    add("explain_tradeoffs", {Piece.BISHOP}, "analysis")

    add("generate_alternatives", {Piece.KNIGHT}, "exploration")
    add("challenge_assumptions", {Piece.KNIGHT}, "exploration")
    add("find_workarounds", {Piece.KNIGHT}, "exploration")
    add("simulate_unusual_paths", {Piece.KNIGHT}, "exploration")
    add("recover_from_blocker", {Piece.KNIGHT}, "exploration")
    add("stress_test_plan", {Piece.KNIGHT}, "exploration")

    add("execute_atomic_task", {Piece.PAWN}, "execution")
    add("collect_data", {Piece.PAWN}, "execution")
    add("summarize_result", {Piece.PAWN}, "execution")
    add("report_blocker", {Piece.PAWN}, "execution")
    add("request_promotion", {Piece.PAWN}, "execution")

    return registry

