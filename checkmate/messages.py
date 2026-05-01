"""Structured message bus and interaction topology."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .models import MessageType, Piece, Priority, new_id, to_plain_data


class TopologyViolation(ValueError):
    """Raised when an agent attempts a disallowed communication path."""


@dataclass
class Message:
    from_agent: str
    to_agent: str
    type: MessageType
    payload: dict[str, Any]
    priority: Priority = Priority.NORMAL
    requires_response: bool = False
    allowed_responses: list[str] = field(default_factory=list)
    message_id: str = field(default_factory=lambda: new_id("msg"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.type.value,
            "priority": self.priority.value,
            "payload": to_plain_data(self.payload),
            "requires_response": self.requires_response,
            "allowed_responses": list(self.allowed_responses),
        }


class MessageBus:
    """Routes messages while enforcing CheckMate communication rules."""

    def __init__(self, agent_pieces: Optional[dict[str, Piece]] = None) -> None:
        self.agent_pieces = agent_pieces or {}
        self._messages: list[Message] = []

    def register_agent(self, agent_id: str, piece: Piece) -> None:
        self.agent_pieces[agent_id] = piece

    def submit(self, message: Message) -> None:
        if not self.can_send(message):
            raise TopologyViolation(
                f"{message.from_agent} cannot send {message.type.value} "
                f"to {message.to_agent}"
            )
        self._messages.append(message)

    def submit_many(self, messages: list[Message]) -> None:
        for message in messages:
            self.submit(message)

    def messages_for(self, agent_id: str) -> list[Message]:
        return [message for message in self._messages if message.to_agent == agent_id]

    def drain_for(self, agent_id: str) -> list[Message]:
        found = self.messages_for(agent_id)
        self._messages = [
            message for message in self._messages if message.to_agent != agent_id
        ]
        return found

    def can_send(self, message: Message) -> bool:
        from_piece = self.agent_pieces.get(message.from_agent)
        to_piece = self.agent_pieces.get(message.to_agent)

        if from_piece is None or to_piece is None:
            return False

        if from_piece == Piece.QUEEN:
            return True

        if from_piece == Piece.KING:
            return to_piece == Piece.QUEEN

        if from_piece == Piece.KNIGHT:
            return True

        if message.type == MessageType.CONFLICT_NOTICE:
            return to_piece in {Piece.QUEEN, Piece.KING}

        if from_piece == Piece.ROOK:
            return to_piece in {Piece.QUEEN, Piece.KING, Piece.ROOK}

        if from_piece == Piece.BISHOP:
            return to_piece in {Piece.QUEEN, Piece.BISHOP}

        if from_piece == Piece.PAWN:
            return to_piece == Piece.QUEEN

        return False

    @property
    def messages(self) -> list[Message]:
        return list(self._messages)
