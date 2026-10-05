import asyncio
from pathlib import Path

from backend.agents.agent_manager import AgentManager
from backend.agents.application_agent import ApplicationAgent
from backend.agents.browser_agent import BrowserAgent
from backend.agents.file_agent import FileAgent
from backend.agents.goal_agent import GoalAgent
from backend.agents.memory_agent import MemoryAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.recovery_agent import RecoveryAgent
from backend.automation.events import EventBus
from backend.automation.executor import AutomationExecutor
from backend.services.llm.interpreter import GoalInterpreter
from backend.memory.database import init_db
from backend.memory.memory_manager import MemoryManager
from backend.planner.task_planner import TaskPlanner
from backend.recovery.recovery_engine import RecoveryEngine
from backend.security.action_registry import AllowedActionRegistry
from backend.security.permission_manager import PermissionManager
from backend.models.schemas import TaskModel, WorkflowPlan


def test_executor_runs_simple_plan(tmp_path: Path):
    init_db()
    registry = AllowedActionRegistry()
    permissions = PermissionManager()
    memory = MemoryManager()
    recovery = RecoveryEngine()
    events = EventBus()

    manager = AgentManager(
        goal_agent=GoalAgent(GoalInterpreter(provider=None)),
        planner_agent=PlannerAgent(TaskPlanner(registry)),
        file_agent=FileAgent(permissions),
        browser_agent=BrowserAgent(),
        application_agent=ApplicationAgent(),
        memory_agent=MemoryAgent(memory),
        recovery_agent=RecoveryAgent(recovery),
    )

    executor = AutomationExecutor(manager, permissions, registry, memory, recovery, events)

    scope = str(tmp_path)
    permissions.grant("file_access", [scope])

    plan = WorkflowPlan(
        workflow_id="wf_exec_1",
        goal="Create folder",
        tasks=[
            TaskModel(
                id="task_1",
                action="create_folder",
                agent="FileAgent",
                parameters={"parent": scope, "name": "demo"},
            )
        ],
        required_capabilities={"file_access": [scope]},
    )

    workflow_id = memory.save_workflow_plan(plan, "Create folder")
    results = asyncio.run(executor.execute_plan(workflow_id, plan))

    assert results[0].status.value in {"COMPLETED", "RECOVERED"}
