from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.services.llm.interpreter import GoalInterpreter


class GoalAgent(BaseAgent):
    name = "GoalAgent"

    def __init__(self, interpreter: GoalInterpreter) -> None:
        self.interpreter = interpreter

    def interpret_goal(self, goal: str) -> dict[str, Any]:
        interpretation = self.interpreter.interpret(goal)
        return interpretation.model_dump()

    def execute(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if action != "interpret_goal":
            raise ValueError(f"Unsupported action: {action}")
        return self.interpret_goal(**parameters)
