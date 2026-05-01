import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checkmate import run_checkmate


if __name__ == "__main__":
    board = run_checkmate(
        "Build a project plan for an API migration",
        constraints=[
            "must preserve uptime",
            "deadline is 2 weeks",
            "use existing team capacity",
        ],
    )
    print(f"status: {board.status.value}")
    print(f"plan: {board.current_plan['plan_id'] if board.current_plan else 'none'}")
    print(f"decisions: {[decision.outcome for decision in board.decisions]}")
    print(f"risks: {[risk.summary for risk in board.risks]}")
