from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.planner.task_planner import TaskPlanner


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"

    def __init__(self, planner: TaskPlanner) -> None:
        self.planner = planner

    def plan_workflow(self, goal: str, tasks: list[dict]) -> dict[str, Any]:
        plan = self.planner.create_plan(goal=goal, tasks=tasks)
        return plan.model_dump()

    def execute(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if action != "plan_workflow":
            raise ValueError(f"Unsupported action: {action}")
        return self.plan_workflow(**parameters)
