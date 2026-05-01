"""Small in-memory memory layer for CheckMate."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .models import Piece


@dataclass
class MemoryRecord:
    key: str
    value: Any
    written_by: str
    piece: Piece
    memory_type: str


@dataclass
class MemoryLayer:
    """Split memory into short-term, long-term, and episodic stores."""

    short_term: dict[str, MemoryRecord] = field(default_factory=dict)
    long_term: dict[str, MemoryRecord] = field(default_factory=dict)
    episodic: dict[str, MemoryRecord] = field(default_factory=dict)

    write_permissions: dict[Piece, set[str]] = field(
        default_factory=lambda: {
            Piece.KING: {"short_term", "long_term", "episodic"},
            Piece.QUEEN: {"short_term", "episodic"},
            Piece.ROOK: {"short_term", "long_term"},
            Piece.BISHOP: {"short_term", "long_term"},
            Piece.KNIGHT: {"short_term", "episodic"},
            Piece.PAWN: {"short_term", "episodic"},
        }
    )

    def write(
        self,
        memory_type: str,
        key: str,
        value: Any,
        written_by: str,
        piece: Piece,
    ) -> None:
        if memory_type not in self.write_permissions[piece]:
            raise PermissionError(f"{piece.value} cannot write {memory_type} memory")
        store = self._store(memory_type)
        store[key] = MemoryRecord(
            key=key,
            value=value,
            written_by=written_by,
            piece=piece,
            memory_type=memory_type,
        )

    def read(self, memory_type: str, key: str) -> Optional[MemoryRecord]:
        return self._store(memory_type).get(key)

    def _store(self, memory_type: str) -> dict[str, MemoryRecord]:
        if memory_type == "short_term":
            return self.short_term
        if memory_type == "long_term":
            return self.long_term
        if memory_type == "episodic":
            return self.episodic
        raise ValueError(f"Unknown memory type: {memory_type}")
