from __future__ import annotations

from dataclasses import dataclass, field

from backend.agents.agent_manager import AgentManager
from backend.automation.events import EventBus
from backend.automation.executor import AutomationExecutor
from backend.core.context_engine import ContextEngine
from backend.learning.learning_engine import LearningEngine
from backend.services.llm.interpreter import GoalInterpreter
from backend.memory.database import init_db
from backend.memory.memory_manager import MemoryManager
from backend.planner.task_planner import TaskPlanner
from backend.recovery.recovery_engine import RecoveryEngine
from backend.security.action_registry import AllowedActionRegistry
from backend.security.permission_manager import PermissionManager


@dataclass
class AIONServices:
    interpreter: GoalInterpreter
    planner: TaskPlanner
    memory: MemoryManager
    learning: LearningEngine
    permissions: PermissionManager
    registry: AllowedActionRegistry
    executor: AutomationExecutor
    context: ContextEngine
    events: EventBus
    plans: dict[str, tuple[int, object]] = field(default_factory=dict)


def build_services() -> AIONServices:
    init_db()
    registry = AllowedActionRegistry()
    memory = MemoryManager()
    permissions = PermissionManager()
    recovery = RecoveryEngine()
    event_bus = EventBus()

    interpreter = GoalInterpreter()
    planner = TaskPlanner(registry)

    from backend.agents.application_agent import ApplicationAgent
    from backend.agents.browser_agent import BrowserAgent
    from backend.agents.file_agent import FileAgent
    from backend.agents.goal_agent import GoalAgent
    from backend.agents.memory_agent import MemoryAgent
    from backend.agents.planner_agent import PlannerAgent
    from backend.agents.recovery_agent import RecoveryAgent

    manager = AgentManager(
        goal_agent=GoalAgent(interpreter),
        planner_agent=PlannerAgent(planner),
        file_agent=FileAgent(permissions),
        browser_agent=BrowserAgent(),
        application_agent=ApplicationAgent(),
        memory_agent=MemoryAgent(memory),
        recovery_agent=RecoveryAgent(recovery),
    )

    executor = AutomationExecutor(
        agent_manager=manager,
        permission_manager=permissions,
        action_registry=registry,
        memory=memory,
        recovery=recovery,
        event_bus=event_bus,
    )

    learning = LearningEngine(memory)
    context = ContextEngine()

    return AIONServices(
        interpreter=interpreter,
        planner=planner,
        memory=memory,
        learning=learning,
        permissions=permissions,
        registry=registry,
        executor=executor,
        context=context,
        events=event_bus,
    )
