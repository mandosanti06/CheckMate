"""Core data models for the CheckMate runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Union
from uuid import uuid4


class TextEnum(str, Enum):
    """Enum that serializes naturally as text."""

    def __str__(self) -> str:
        return self.value


class Piece(TextEnum):
    KING = "king"
    QUEEN = "queen"
    ROOK = "rook"
    BISHOP = "bishop"
    KNIGHT = "knight"
    PAWN = "pawn"


class ReasoningMode(TextEnum):
    EVALUATIVE = "evaluative"
    EXECUTIVE = "executive"
    LINEAR = "linear"
    DIAGONAL = "diagonal"
    NONLINEAR = "nonlinear"
    ATOMIC = "atomic"


class AgentStatus(TextEnum):
    SUCCESS = "success"
    BLOCKED = "blocked"
    NEEDS_CLARIFICATION = "needs_clarification"
    CONFLICT = "conflict"


class RuntimeStatus(TextEnum):
    IDLE = "idle"
    PLANNING = "planning"
    VALIDATING = "validating"
    EXECUTING = "executing"
    CHECK = "check"
    CHECKMATE = "checkmate"
    COMPLETE = "complete"


class MessageType(TextEnum):
    GOAL_ORDER = "goal_order"
    TASK_ASSIGNMENT = "task_assignment"
    ANALYSIS_REPORT = "analysis_report"
    CONSTRAINT_REPORT = "constraint_report"
    CREATIVE_PROPOSAL = "creative_proposal"
    EXECUTION_REPORT = "execution_report"
    CONFLICT_NOTICE = "conflict_notice"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_DECISION = "approval_decision"
    VETO_NOTICE = "veto_notice"
    PROMOTION_REQUEST = "promotion_request"


class Priority(TextEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ConflictType(TextEnum):
    GOAL = "goal"
    CONSTRAINT = "constraint"
    EVIDENCE = "evidence"
    PRIORITY = "priority"
    EXECUTION = "execution"
    INTERPRETATION = "interpretation"


class Severity(TextEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConflictOutcome(TextEnum):
    ACCEPT_PLAN = "accept_plan"
    REVISE_PLAN = "revise_plan"
    SPLIT_PLAN = "split_plan"
    RUN_EXPERIMENT = "run_experiment"
    ESCALATE_TO_KING = "escalate_to_king"
    DECLARE_CHECK = "declare_check"
    DECLARE_CHECKMATE = "declare_checkmate"


class TaskStatus(TextEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def to_plain_data(value: Any) -> Any:
    """Convert dataclasses and enums into JSON-friendly values."""

    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: to_plain_data(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [to_plain_data(item) for item in value]
    if isinstance(value, tuple):
        return [to_plain_data(item) for item in value]
    if isinstance(value, dict):
        return {key: to_plain_data(item) for key, item in value.items()}
    return value


@dataclass
class Constraint:
    description: str
    hard: bool = True
    source: str = "king"
    id: str = field(default_factory=lambda: new_id("constraint"))

    @classmethod
    def from_value(cls, value: Union[str, Dict[str, Any], "Constraint"]) -> "Constraint":
        if isinstance(value, Constraint):
            return value
        if isinstance(value, str):
            return cls(description=value)
        return cls(**value)


@dataclass
class Task:
    title: str
    description: str
    assigned_to: str
    id: str = field(default_factory=lambda: new_id("task"))
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


@dataclass
class Risk:
    summary: str
    severity: Severity = Severity.MEDIUM
    source: str = "system"
    mitigations: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: new_id("risk"))


@dataclass
class Decision:
    made_by: str
    outcome: str
    rationale: str
    id: str = field(default_factory=lambda: new_id("decision"))
    timestamp: str = field(default_factory=utc_now_iso)


@dataclass
class Claim:
    claim: str
    evidence: list[Any] = field(default_factory=list)
    risk_if_wrong: str = ""
    confidence: float = 0.0
    preferred_resolution: str = ""

    def __post_init__(self) -> None:
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class Conflict:
    conflict_type: ConflictType
    agents_involved: list[str]
    severity: Severity
    blocking: bool
    summary: str
    claims: list[Claim] = field(default_factory=list)
    id: str = field(default_factory=lambda: new_id("conflict"))
    resolved: bool = False
    resolution_outcome: Optional[ConflictOutcome] = None


@dataclass
class AgentInput:
    goal: str
    context: dict[str, Any]
    constraints: list[dict[str, Any]]
    available_tools: list[str]
    messages: list[dict[str, Any]]


@dataclass
class AgentOutput:
    status: AgentStatus
    summary: str
    findings: list[Any] = field(default_factory=list)
    recommendations: list[Any] = field(default_factory=list)
    risks: list[Any] = field(default_factory=list)
    proposed_actions: list[Any] = field(default_factory=list)
    confidence: float = 0.0

    def __post_init__(self) -> None:
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class AgentMetadata:
    timestamp: str
    reasoning_mode: ReasoningMode
    dependencies: list[str] = field(default_factory=list)
    escalation_target: str = "none"
