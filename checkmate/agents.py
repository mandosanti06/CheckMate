"""Piece agents for the CheckMate runtime."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional

from .board import BoardState
from .messages import Message
from .models import (
    AgentInput,
    AgentOutput,
    AgentStatus,
    Claim,
    Conflict,
    ConflictType,
    Decision,
    MessageType,
    Piece,
    Priority,
    ReasoningMode,
    Risk,
    Severity,
    Task,
    TaskStatus,
    new_id,
)
from .tools import ToolRegistry, default_tool_registry


@dataclass
class AgentRunResult:
    agent_id: str
    piece: Piece
    output: AgentOutput
    updates: dict[str, Any] = field(default_factory=dict)
    messages: list[Message] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    status: str = "done"


class PieceAgent:
    """Base interface shared by every piece-agent."""

    def __init__(
        self,
        agent_id: str,
        piece: Piece,
        role: str,
        reasoning_mode: ReasoningMode,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:
        self.agent_id = agent_id
        self.piece = piece
        self.role = role
        self.reasoning_mode = reasoning_mode
        self.tool_registry = tool_registry or default_tool_registry()

    def build_input(self, board: BoardState, messages: list[Message]) -> AgentInput:
        return AgentInput(
            goal=board.goal,
            context=board.context,
            constraints=[constraint.__dict__ for constraint in board.constraints],
            available_tools=self.tool_registry.allowed_tools_for(self.piece),
            messages=[message.to_dict() for message in messages],
        )

    def run(
        self,
        board: BoardState,
        messages: list[Message],
        assigned_task: Optional[dict[str, Any]] = None,
    ) -> AgentRunResult:
        raise NotImplementedError

    def _output(
        self,
        status: AgentStatus,
        summary: str,
        findings: Optional[list[Any]] = None,
        recommendations: Optional[list[Any]] = None,
        risks: Optional[list[Any]] = None,
        proposed_actions: Optional[list[Any]] = None,
        confidence: float = 0.75,
    ) -> AgentOutput:
        return AgentOutput(
            status=status,
            summary=summary,
            findings=findings or [],
            recommendations=recommendations or [],
            risks=risks or [],
            proposed_actions=proposed_actions or [],
            confidence=confidence,
        )

    def _message(
        self,
        to_agent: str,
        message_type: MessageType,
        payload: dict[str, Any],
        priority: Priority = Priority.NORMAL,
        requires_response: bool = False,
        allowed_responses: Optional[list[str]] = None,
    ) -> Message:
        return Message(
            from_agent=self.agent_id,
            to_agent=to_agent,
            type=message_type,
            payload=payload,
            priority=priority,
            requires_response=requires_response,
            allowed_responses=allowed_responses or [],
        )


class KingAgent(PieceAgent):
    def __init__(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        super().__init__(
            "king",
            Piece.KING,
            "governance",
            ReasoningMode.EVALUATIVE,
            tool_registry,
        )

    def run(
        self,
        board: BoardState,
        messages: list[Message],
        assigned_task: Optional[dict[str, Any]] = None,
    ) -> AgentRunResult:
        self.build_input(board, messages)
        if not board.goal.strip():
            return AgentRunResult(
                self.agent_id,
                self.piece,
                self._output(
                    AgentStatus.NEEDS_CLARIFICATION,
                    "No objective was provided.",
                    proposed_actions=["Ask for a clear objective."],
                    confidence=1.0,
                ),
                status="blocked",
            )

        if board.status.value == "checkmate":
            decision = Decision(
                made_by=self.agent_id,
                outcome="checkmate",
                rationale=(
                    "No valid plan satisfies the current objective and hard "
                    "constraints."
                ),
            )
            return AgentRunResult(
                self.agent_id,
                self.piece,
                self._output(
                    AgentStatus.BLOCKED,
                    "Declared checkmate under the current constraints.",
                    proposed_actions=[
                        "Relax the objective.",
                        "Relax one or more hard constraints.",
                        "Redefine success criteria.",
                    ],
                    confidence=0.95,
                ),
                updates={"decisions_to_add": [decision]},
                status="blocked",
            )

        if board.status.value == "check":
            decision = Decision(
                made_by=self.agent_id,
                outcome="check",
                rationale=(
                    "The goal is threatened by a recoverable conflict. Execution "
                    "must pause until the Queen revises the plan."
                ),
            )
            reply = self._message(
                "queen",
                MessageType.APPROVAL_DECISION,
                {"decision": "revise", "reason": "check state is active"},
                priority=Priority.HIGH,
            )
            return AgentRunResult(
                self.agent_id,
                self.piece,
                self._output(
                    AgentStatus.CONFLICT,
                    "Declared check and requested replanning.",
                    findings=["A recoverable threat is active."],
                    proposed_actions=["Revise the plan before approval."],
                    confidence=0.9,
                ),
                updates={"decisions_to_add": [decision], "status": "check"},
                messages=[reply],
                status="needs_review",
            )

        approval_requests = [
            message for message in messages if message.type == MessageType.APPROVAL_REQUEST
        ]
        if board.current_plan and approval_requests and not board.has_blocking_conflicts():
            decision = Decision(
                made_by=self.agent_id,
                outcome="approved",
                rationale="The plan satisfies the objective and no Rook veto is active.",
            )
            reply = self._message(
                "queen",
                MessageType.APPROVAL_DECISION,
                {"decision": "approved", "plan_id": board.current_plan["plan_id"]},
                priority=Priority.HIGH,
            )
            return AgentRunResult(
                self.agent_id,
                self.piece,
                self._output(
                    AgentStatus.SUCCESS,
                    "Approved the synthesized plan.",
                    findings=["Objective is clear.", "No hard feasibility veto is active."],
                    confidence=0.9,
                ),
                updates={
                    "decisions_to_add": [decision],
                    "status": "executing",
                },
                messages=[reply],
            )

        order = self._message(
            "queen",
            MessageType.GOAL_ORDER,
            {
                "goal": board.goal,
                "constraints": [constraint.description for constraint in board.constraints],
                "success_criteria": [
                    "A plan exists.",
                    "Hard constraints are respected.",
                    "Execution reports are captured.",
                ],
            },
            priority=Priority.HIGH,
            requires_response=True,
            allowed_responses=["acknowledge", "request_more_detail", "escalate"],
        )
        return AgentRunResult(
            self.agent_id,
            self.piece,
            self._output(
                AgentStatus.SUCCESS,
                "Objective and governance criteria are defined.",
                findings=[board.goal],
                confidence=0.9,
            ),
            updates={"status": "planning"},
            messages=[order],
        )


class QueenAgent(PieceAgent):
    def __init__(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        super().__init__(
            "queen",
            Piece.QUEEN,
            "orchestration",
            ReasoningMode.EXECUTIVE,
            tool_registry,
        )

    def run(
        self,
        board: BoardState,
        messages: list[Message],
        assigned_task: Optional[dict[str, Any]] = None,
    ) -> AgentRunResult:
        self.build_input(board, messages)
        phase = (assigned_task or {}).get("phase", "decompose")
        if phase == "synthesize":
            return self._synthesize(board)
        return self._decompose(board)

    def _decompose(self, board: BoardState) -> AgentRunResult:
        task_specs = [
            (
                "task_interpret_causal",
                "Analyze causal implications",
                "Identify root causes, dependencies over time, and second-order risk.",
                "bishop_causal",
            ),
            (
                "task_interpret_pattern",
                "Detect reusable patterns",
                "Map the objective to reusable strategies and historical analogies.",
                "bishop_pattern",
            ),
            (
                "task_validate_logic",
                "Validate logical constraints",
                "Check internal consistency, contradictions, and dependency chains.",
                "rook_logic",
            ),
            (
                "task_validate_resources",
                "Validate execution constraints",
                "Check resources, time, external systems, and execution capacity.",
                "rook_resource",
            ),
            (
                "task_explore_creative",
                "Generate alternate paths",
                "Propose novel or simplified approaches.",
                "knight_creative",
            ),
            (
                "task_explore_recovery",
                "Generate recovery paths",
                "Find fallbacks, workarounds, and emergency replanning options.",
                "knight_recovery",
            ),
        ]
        existing_ids = {task.id for task in board.tasks}
        tasks = [
            Task(id=task_id, title=title, description=description, assigned_to=agent_id)
            for task_id, title, description, agent_id in task_specs
            if task_id not in existing_ids
        ]
        messages = [
            self._message(
                task.assigned_to,
                MessageType.TASK_ASSIGNMENT,
                {"task_id": task.id, "title": task.title, "description": task.description},
                priority=Priority.NORMAL,
                requires_response=True,
                allowed_responses=["acknowledge", "conflict", "blocked"],
            )
            for task in tasks
        ]
        return AgentRunResult(
            self.agent_id,
            self.piece,
            self._output(
                AgentStatus.SUCCESS,
                "Decomposed the objective into analysis, validation, and exploration tasks.",
                findings=[task.id for task in tasks],
                confidence=0.85,
            ),
            updates={"tasks_to_add": tasks},
            messages=messages,
        )

    def _synthesize(self, board: BoardState) -> AgentRunResult:
        if board.status.value == "check" or board.has_blocking_conflicts():
            return AgentRunResult(
                self.agent_id,
                self.piece,
                self._output(
                    AgentStatus.CONFLICT,
                    "Cannot synthesize a final plan while check or blocking conflicts exist.",
                    risks=[conflict.summary for conflict in board.conflicts if conflict.blocking],
                    proposed_actions=["Escalate to King for check or checkmate decision."],
                    confidence=0.9,
                ),
                status="needs_review",
            )

        execution_tasks = [
            Task(
                id="task_execute_goal",
                title="Execute approved objective",
                description="Carry out the approved plan as atomic work.",
                assigned_to="pawn_operations",
                dependencies=["task_validate_logic", "task_validate_resources"],
            ),
            Task(
                id="task_quality_check",
                title="Verify execution quality",
                description="Review the execution evidence and report defects.",
                assigned_to="pawn_qa",
                dependencies=["task_execute_goal"],
            ),
        ]
        existing_ids = {task.id for task in board.tasks}
        execution_tasks = [task for task in execution_tasks if task.id not in existing_ids]
        plan = {
            "plan_id": new_id("plan"),
            "objective": board.goal,
            "constraints": [constraint.description for constraint in board.constraints],
            "steps": [
                {
                    "task_id": task.id,
                    "title": task.title,
                    "assigned_to": task.assigned_to,
                    "dependencies": task.dependencies,
                }
                for task in board.tasks + execution_tasks
            ],
            "risks": [risk.summary for risk in board.risks],
            "agent_context": board.context.get("agent_outputs", {}),
        }
        request = self._message(
            "king",
            MessageType.APPROVAL_REQUEST,
            {"plan_id": plan["plan_id"], "summary": "Plan ready for approval."},
            priority=Priority.HIGH,
            requires_response=True,
            allowed_responses=["approve", "reject", "revise", "checkmate"],
        )
        return AgentRunResult(
            self.agent_id,
            self.piece,
            self._output(
                AgentStatus.SUCCESS,
                "Synthesized an executable plan from agent outputs.",
                findings=[plan["plan_id"]],
                risks=plan["risks"],
                proposed_actions=["Submit synthesized plan to King for approval."],
                confidence=0.88,
            ),
            updates={"current_plan": plan, "tasks_to_add": execution_tasks},
            messages=[request],
        )


class BishopAgent(PieceAgent):
    def __init__(
        self,
        agent_id: str,
        role: str,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:
        super().__init__(agent_id, Piece.BISHOP, role, ReasoningMode.DIAGONAL, tool_registry)

    def run(
        self,
        board: BoardState,
        messages: list[Message],
        assigned_task: Optional[dict[str, Any]] = None,
    ) -> AgentRunResult:
        self.build_input(board, messages)
        if self.role == "causal_reasoning":
            return self._causal(board)
        return self._pattern(board)

    def _causal(self, board: BoardState) -> AgentRunResult:
        findings = [
            "Outcome quality depends on preserving the King constraints through every phase.",
            "Late constraint discovery creates rework pressure on the Queen and Pawns.",
        ]
        risks: list[Risk] = []
        constraint_text = " ".join(constraint.description.lower() for constraint in board.constraints)
        if "deadline" in constraint_text or "week" in constraint_text:
            risks.append(
                Risk(
                    "Timeline pressure may force the Queen to collapse roles into a monolith.",
                    severity=Severity.MEDIUM,
                    source=self.agent_id,
                    mitigations=["Keep Rook validation before King approval."],
                )
            )
        if "uptime" in constraint_text or "no downtime" in constraint_text:
            risks.append(
                Risk(
                    "Availability constraints require rollback and staged execution paths.",
                    severity=Severity.HIGH,
                    source=self.agent_id,
                    mitigations=["Ask Recovery Knight for fallback paths."],
                )
            )
        report = self._message(
            "queen",
            MessageType.ANALYSIS_REPORT,
            {
                "claim": "The objective is sensitive to second-order constraint drift.",
                "evidence": findings,
                "recommended_action": "Preserve validation gates before execution.",
            },
        )
        return AgentRunResult(
            self.agent_id,
            self.piece,
            self._output(
                AgentStatus.SUCCESS,
                "Causal analysis completed.",
                findings=findings,
                risks=[risk.summary for risk in risks],
                recommendations=["Make recovery criteria explicit before Pawns execute."],
                confidence=0.78,
            ),
            updates={"risks_to_add": risks},
            messages=[report],
        )

    def _pattern(self, board: BoardState) -> AgentRunResult:
        goal = board.goal.lower()
        recommendations = [
            "Use the standard loop: interpret, validate, explore, synthesize, approve, execute.",
            "Store failed alternatives so future Knight work starts with more context.",
        ]
        if "project plan" in goal:
            recommendations.append("Represent the plan as phases, dependencies, risks, and evidence.")
        if "api" in goal or "migration" in goal:
            recommendations.append("Prefer a staged rollout with rollback criteria and QA checkpoints.")
        report = self._message(
            "queen",
            MessageType.ANALYSIS_REPORT,
            {
                "claim": "The objective matches a reusable governed-planning pattern.",
                "evidence": recommendations,
                "recommended_action": "Synthesize a phase-based plan.",
            },
        )
        return AgentRunResult(
            self.agent_id,
            self.piece,
            self._output(
                AgentStatus.SUCCESS,
                "Pattern analysis completed.",
                findings=["Reusable governance/synthesis/validation loop detected."],
                recommendations=recommendations,
                confidence=0.82,
            ),
            messages=[report],
        )


class RookAgent(PieceAgent):
    def __init__(
        self,
        agent_id: str,
        role: str,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:
        super().__init__(agent_id, Piece.ROOK, role, ReasoningMode.LINEAR, tool_registry)

    def run(
        self,
        board: BoardState,
        messages: list[Message],
        assigned_task: Optional[dict[str, Any]] = None,
    ) -> AgentRunResult:
        self.build_input(board, messages)
        if self.role == "logical_constraints":
            return self._validate_logic(board)
        return self._validate_resources(board)

    def _validate_logic(self, board: BoardState) -> AgentRunResult:
        contradiction = _find_constraint_contradiction(
            [constraint.description for constraint in board.hard_constraints()]
        )
        if contradiction:
            conflict = Conflict(
                conflict_type=ConflictType.CONSTRAINT,
                agents_involved=[self.agent_id, "king", "queen"],
                severity=Severity.CRITICAL,
                blocking=True,
                summary=contradiction,
                claims=[
                    Claim(
                        claim=contradiction,
                        evidence=[constraint.description for constraint in board.hard_constraints()],
                        risk_if_wrong="The system may approve an internally impossible plan.",
                        confidence=0.9,
                        preferred_resolution="declare_checkmate",
                    )
                ],
            )
            vetoes = [
                self._message(
                    "queen",
                    MessageType.VETO_NOTICE,
                    {"issue": contradiction, "blocked_tasks": [task.id for task in board.tasks]},
                    priority=Priority.CRITICAL,
                    requires_response=True,
                    allowed_responses=["acknowledge", "escalate"],
                ),
                self._message(
                    "king",
                    MessageType.VETO_NOTICE,
                    {"issue": contradiction, "blocked_tasks": [task.id for task in board.tasks]},
                    priority=Priority.CRITICAL,
                    requires_response=True,
                    allowed_responses=["acknowledge", "relax_constraint"],
                ),
            ]
            return AgentRunResult(
                self.agent_id,
                self.piece,
                self._output(
                    AgentStatus.CONFLICT,
                    "Logical constraints are invalid.",
                    findings=[contradiction],
                    risks=["Planning cannot continue with contradictory hard constraints."],
                    proposed_actions=["Declare checkmate or relax constraints."],
                    confidence=0.9,
                ),
                updates={"conflicts_to_add": [conflict]},
                messages=vetoes,
                status="blocked",
            )

        report = self._message(
            "queen",
            MessageType.CONSTRAINT_REPORT,
            {
                "status": "valid",
                "claim": "No direct hard-constraint contradiction detected.",
            },
        )
        return AgentRunResult(
            self.agent_id,
            self.piece,
            self._output(
                AgentStatus.SUCCESS,
                "Logical constraints validated.",
                findings=["No direct hard-constraint contradictions detected."],
                confidence=0.86,
            ),
            messages=[report],
        )

    def _validate_resources(self, board: BoardState) -> AgentRunResult:
        goal = board.goal.lower()
        constraints = " ".join(constraint.description.lower() for constraint in board.constraints)
        risks: list[Risk] = []
        if ("zero budget" in constraints or "no budget" in constraints) and any(
            word in goal for word in ["purchase", "paid", "hire", "vendor"]
        ):
            risks.append(
                Risk(
                    "Objective may require spend, but budget is constrained to zero.",
                    severity=Severity.HIGH,
                    source=self.agent_id,
                    mitigations=["Use existing resources or relax the budget constraint."],
                )
            )
        if "external" in constraints and "cannot" in constraints:
            risks.append(
                Risk(
                    "External-system restrictions may reduce available execution tools.",
                    severity=Severity.MEDIUM,
                    source=self.agent_id,
                    mitigations=["Route execution through approved internal tools."],
                )
            )
        report = self._message(
            "queen",
            MessageType.CONSTRAINT_REPORT,
            {
                "status": "risk" if risks else "valid",
                "risks": [risk.summary for risk in risks],
            },
        )
        return AgentRunResult(
            self.agent_id,
            self.piece,
            self._output(
                AgentStatus.SUCCESS,
                "Execution constraints validated.",
                findings=["Resources and execution capacity were checked."],
                risks=[risk.summary for risk in risks],
                confidence=0.8,
            ),
            updates={"risks_to_add": risks},
            messages=[report],
        )


class KnightAgent(PieceAgent):
    def __init__(
        self,
        agent_id: str,
        role: str,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:
        super().__init__(agent_id, Piece.KNIGHT, role, ReasoningMode.NONLINEAR, tool_registry)

    def run(
        self,
        board: BoardState,
        messages: list[Message],
        assigned_task: Optional[dict[str, Any]] = None,
    ) -> AgentRunResult:
        self.build_input(board, messages)
        if self.role == "creative_generator":
            return self._creative(board)
        return self._recovery(board)

    def _creative(self, board: BoardState) -> AgentRunResult:
        proposals = [
            "Run a thin vertical slice before committing to the full plan.",
            "Treat each Rook veto as an explicit design input instead of a failure.",
            "Promote recurring Pawn work into a specialist role when evidence accumulates.",
        ]
        message = self._message(
            "queen",
            MessageType.CREATIVE_PROPOSAL,
            {"alternatives": proposals},
        )
        return AgentRunResult(
            self.agent_id,
            self.piece,
            self._output(
                AgentStatus.SUCCESS,
                "Generated nonlinear alternatives.",
                recommendations=proposals,
                confidence=0.76,
            ),
            messages=[message],
        )

    def _recovery(self, board: BoardState) -> AgentRunResult:
        recovery_paths = [
            "If a deadline fails, split the plan into minimum viable and deferred scopes.",
            "If information is missing, assign Research Pawn before plan approval.",
            "If a hard constraint blocks execution, ask King to relax success criteria.",
        ]
        if board.conflicts:
            recovery_paths.append("For current conflicts, run a narrow experiment before replanning.")
        message = self._message(
            "queen",
            MessageType.CREATIVE_PROPOSAL,
            {"recovery_paths": recovery_paths},
            priority=Priority.HIGH if board.conflicts else Priority.NORMAL,
        )
        return AgentRunResult(
            self.agent_id,
            self.piece,
            self._output(
                AgentStatus.SUCCESS,
                "Generated recovery paths.",
                recommendations=recovery_paths,
                confidence=0.8,
            ),
            messages=[message],
        )


class PawnAgent(PieceAgent):
    def __init__(
        self,
        agent_id: str,
        role: str,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:
        super().__init__(agent_id, Piece.PAWN, role, ReasoningMode.ATOMIC, tool_registry)

    def run(
        self,
        board: BoardState,
        messages: list[Message],
        assigned_task: Optional[dict[str, Any]] = None,
    ) -> AgentRunResult:
        self.build_input(board, messages)
        tasks = [
            task
            for task in board.tasks_for(self.agent_id)
            if task.status in {TaskStatus.PENDING, TaskStatus.IN_PROGRESS}
        ]
        if not tasks:
            return AgentRunResult(
                self.agent_id,
                self.piece,
                self._output(
                    AgentStatus.SUCCESS,
                    "No atomic task was assigned.",
                    findings=["Idle observer state."],
                    confidence=0.95,
                ),
            )
        completed: dict[str, TaskStatus] = {}
        evidence: dict[str, list[str]] = {}
        reports: list[Message] = []
        blocked: list[str] = []
        completed_task_ids = {
            task.id for task in board.tasks if task.status == TaskStatus.COMPLETED
        }
        for task in tasks:
            unmet = [
                dependency
                for dependency in task.dependencies
                if dependency not in completed_task_ids and dependency not in completed
            ]
            if unmet:
                completed[task.id] = TaskStatus.BLOCKED
                evidence[task.id] = [f"Blocked by unmet dependencies: {', '.join(unmet)}"]
                blocked.append(task.id)
                continue
            completed[task.id] = TaskStatus.COMPLETED
            evidence[task.id] = [f"{self.agent_id} completed {task.title}."]
            reports.append(
                self._message(
                    "queen",
                    MessageType.EXECUTION_REPORT,
                    {
                        "task_id": task.id,
                        "status": "completed",
                        "evidence": evidence[task.id],
                    },
                )
            )
        status = AgentStatus.BLOCKED if blocked else AgentStatus.SUCCESS
        return AgentRunResult(
            self.agent_id,
            self.piece,
            self._output(
                status,
                "Executed assigned atomic tasks." if not blocked else "Some tasks are blocked.",
                findings=list(completed.keys()),
                risks=blocked,
                confidence=0.9,
            ),
            updates={"task_statuses": completed, "task_evidence": evidence},
            messages=reports,
            status="blocked" if blocked else "done",
        )


def _normalize_action(text: str) -> str:
    text = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    text = re.sub(r"\b(must|should|required|requires|require|cannot|can not|use|using)\b", " ", text)
    text = re.sub(r"\b(no|not|the|a|an|to|on|with|without)\b", " ", text)
    text = text.replace("apis", "api")
    return " ".join(text.split())


def _find_constraint_contradiction(constraints: list[str]) -> Optional[str]:
    positive: dict[str, str] = {}
    negative: dict[str, str] = {}

    for raw in constraints:
        text = raw.lower()
        if re.search(r"\b(must|requires|required)\b", text) and not re.search(
            r"\b(must not|cannot|can not|no)\b", text
        ):
            positive[_normalize_action(text)] = raw
        if re.search(r"\b(must not|cannot|can not|no)\b", text):
            negative[_normalize_action(text)] = raw

    for action, pos_text in positive.items():
        if action in negative and action:
            return (
                "Hard constraints contradict each other: "
                f"'{pos_text}' conflicts with '{negative[action]}'."
            )
    return None


def default_agents(tool_registry: Optional[ToolRegistry] = None) -> list[PieceAgent]:
    registry = tool_registry or default_tool_registry()
    return [
        KingAgent(registry),
        QueenAgent(registry),
        RookAgent("rook_logic", "logical_constraints", registry),
        RookAgent("rook_resource", "execution_constraints", registry),
        BishopAgent("bishop_causal", "causal_reasoning", registry),
        BishopAgent("bishop_pattern", "pattern_recognition", registry),
        KnightAgent("knight_creative", "creative_generator", registry),
        KnightAgent("knight_recovery", "constraint_breaker", registry),
        PawnAgent("pawn_research", "research", registry),
        PawnAgent("pawn_writing", "writing", registry),
        PawnAgent("pawn_coding", "coding", registry),
        PawnAgent("pawn_design", "design", registry),
        PawnAgent("pawn_data", "data", registry),
        PawnAgent("pawn_communication", "communication", registry),
        PawnAgent("pawn_operations", "operations", registry),
        PawnAgent("pawn_qa", "qa", registry),
    ]
