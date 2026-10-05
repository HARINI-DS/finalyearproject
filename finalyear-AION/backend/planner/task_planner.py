from __future__ import annotations

from uuid import uuid4

from backend.security.action_registry import AllowedActionRegistry
from backend.models.schemas import TaskModel, WorkflowPlan


class TaskPlanner:
    def __init__(self, registry: AllowedActionRegistry) -> None:
        self.registry = registry

    def create_plan(self, goal: str, tasks: list[dict]) -> WorkflowPlan:
        task_models = [TaskModel.model_validate(task) for task in tasks]
        required_capabilities: dict[str, list[str]] = {}

        for task in task_models:
            rule = self.registry.get_rule(task.action)
            required_capabilities.setdefault(rule.capability, [])

            scope = (
                task.parameters.get("directory")
                or task.parameters.get("destination")
                or task.parameters.get("destination_directory")
                or "global"
            )
            if scope not in required_capabilities[rule.capability]:
                required_capabilities[rule.capability].append(scope)

            if rule.destructive:
                task.requires_confirmation = True

        return WorkflowPlan(
            workflow_id=uuid4().hex,
            goal=goal,
            tasks=task_models,
            required_capabilities=required_capabilities,
        )
