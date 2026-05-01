import unittest

from checkmate import (
    BoardState,
    Conflict,
    ConflictType,
    ExecutionEngine,
    MessageType,
    Piece,
    Priority,
    RuntimeStatus,
    Severity,
    ToolPermissionError,
    default_tool_registry,
)
from checkmate.messages import Message, MessageBus, TopologyViolation


class CheckMateRuntimeTests(unittest.TestCase):
    def test_runtime_creates_approved_plan(self):
        board = ExecutionEngine.default().run(
            "Build a project plan for an API migration",
            constraints=[
                "must preserve uptime",
                "deadline is 2 weeks",
                "use existing team capacity",
            ],
        )

        self.assertEqual(board.status, RuntimeStatus.COMPLETE)
        self.assertIsNotNone(board.current_plan)
        self.assertIn("approved", [decision.outcome for decision in board.decisions])
        self.assertIn("task_execute_goal", [task.id for task in board.tasks])

    def test_contradictory_hard_constraints_declare_checkmate(self):
        board = ExecutionEngine.default().run(
            "Build an integration",
            constraints=[
                "must use external API",
                "cannot use external API",
            ],
        )

        self.assertEqual(board.status, RuntimeStatus.CHECKMATE)
        self.assertTrue(board.conflicts)
        self.assertIn("checkmate", [decision.outcome for decision in board.decisions])

    def test_tool_registry_blocks_king_execution(self):
        registry = default_tool_registry()

        with self.assertRaises(ToolPermissionError):
            registry.assert_allowed(Piece.KING, "execute_atomic_task")

    def test_message_topology_blocks_pawn_to_pawn(self):
        bus = MessageBus({"pawn_a": Piece.PAWN, "pawn_b": Piece.PAWN})
        with self.assertRaises(TopologyViolation):
            bus.submit(
                Message(
                    from_agent="pawn_a",
                    to_agent="pawn_b",
                    type=MessageType.EXECUTION_REPORT,
                    priority=Priority.NORMAL,
                    payload={"status": "done"},
                )
            )

    def test_knight_can_interrupt_any_agent(self):
        bus = MessageBus({"knight": Piece.KNIGHT, "rook": Piece.ROOK})
        bus.submit(
            Message(
                from_agent="knight",
                to_agent="rook",
                type=MessageType.CREATIVE_PROPOSAL,
                priority=Priority.HIGH,
                payload={"alternative": "Run a narrow experiment first."},
            )
        )

        self.assertEqual(len(bus.messages_for("rook")), 1)

    def test_check_state_blocks_final_approval(self):
        engine = ExecutionEngine.default()
        board = BoardState("Ship a risky change")
        board.add_conflict(
            Conflict(
                conflict_type=ConflictType.EXECUTION,
                agents_involved=["pawn_operations"],
                severity=Severity.HIGH,
                blocking=True,
                summary="Execution failed but recovery may be possible.",
            )
        )

        engine.run_board(board)

        self.assertEqual(board.status, RuntimeStatus.CHECK)
        self.assertNotIn("approved", [decision.outcome for decision in board.decisions])


if __name__ == "__main__":
    unittest.main()
