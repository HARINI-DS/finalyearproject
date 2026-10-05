from __future__ import annotations

import asyncio
import time
from pathlib import Path

from backend.agents.agent_manager import AgentManager
from backend.memory.memory_manager import MemoryManager
from backend.recovery.recovery_engine import RecoveryEngine
from backend.security.action_registry import AllowedActionRegistry
from backend.security.permission_manager import PermissionManager
from backend.models.schemas import ExecutionResult, ExecutionStatus, TaskModel, WorkflowPlan
from backend.automation.events import EventBus


class AutomationExecutor:
    def __init__(
        self,
        agent_manager: AgentManager,
        permission_manager: PermissionManager,
        action_registry: AllowedActionRegistry,
        memory: MemoryManager,
        recovery: RecoveryEngine,
        event_bus: EventBus,
    ) -> None:
        self.agent_manager = agent_manager
        self.permission_manager = permission_manager
        self.action_registry = action_registry
        self.memory = memory
        self.recovery = recovery
        self.event_bus = event_bus

    def _required_scope(self, task: TaskModel) -> str:
        return (
            task.parameters.get("path")
            or task.parameters.get("parent")
            or task.parameters.get("directory")
            or task.parameters.get("destination")
            or task.parameters.get("destination_directory")
            or task.parameters.get("url")
            or "global"
        )

    async def execute_plan(self, workflow_db_id: int, plan: WorkflowPlan) -> list[ExecutionResult]:
        results: list[ExecutionResult] = []
        raw_outputs: dict[str, dict] = {}

        for task in plan.tasks:
            start = time.perf_counter()
            await self.event_bus.publish(
                plan.workflow_id,
                {
                    "task_id": task.id,
                    "status": "RUNNING",
                    "message": f"Running {task.action}",
                },
            )

            try:
                rule = self.action_registry.get_rule(task.action)
                scope = self._required_scope(task)
                if rule.capability == "file_access" and scope != "global":
                    scope_path = str(Path(scope).resolve())
                else:
                    scope_path = scope

                if not self.permission_manager.has_permission(rule.capability, scope_path):
                    raise PermissionError(
                        f"Permission missing for capability={rule.capability}, scope={scope_path}"
                    )

                agent = self.agent_manager.get(rule.agent)

                params = dict(task.parameters)
                if task.action == "move_files" and params.get("files") == "__from_task_1__":
                    discovered = raw_outputs.get("task_1", {}).get("files", [])
                    params["files"] = discovered

                payload = agent.execute(task.action, params)

                execution_time = time.perf_counter() - start
                result = ExecutionResult(
                    task_id=task.id,
                    status=ExecutionStatus.COMPLETED,
                    agent=rule.agent,
                    message=str(payload),
                    execution_time=execution_time,
                )
                raw_outputs[task.id] = payload
            except Exception as exc:
                recovery = self.recovery.recover(task.action, task.parameters, str(exc))
                status = (
                    ExecutionStatus.RECOVERED
                    if recovery.get("status") == "RECOVERED"
                    else ExecutionStatus.FAILED
                )
                result = ExecutionResult(
                    task_id=task.id,
                    status=status,
                    agent=self.action_registry.get_rule(task.action).agent,
                    message=recovery.get("message", "Execution failed"),
                    execution_time=time.perf_counter() - start,
                    error=str(exc),
                    recovery=recovery,
                )

            self.memory.record_execution(workflow_db_id, task.action, result)
            results.append(result)
            await self.event_bus.publish(
                plan.workflow_id,
                {
                    "task_id": result.task_id,
                    "status": result.status.value,
                    "message": result.message,
                    "error": result.error,
                },
            )

            if result.status == ExecutionStatus.FAILED:
                break

        await self.event_bus.publish(
            plan.workflow_id,
            {"status": "COMPLETED", "message": "Workflow execution finished"},
        )
        return results
