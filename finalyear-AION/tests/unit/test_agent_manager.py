from backend.agents.agent_manager import AgentManager
from backend.agents.application_agent import ApplicationAgent
from backend.agents.browser_agent import BrowserAgent
from backend.agents.file_agent import FileAgent
from backend.agents.goal_agent import GoalAgent
from backend.agents.memory_agent import MemoryAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.recovery_agent import RecoveryAgent
from backend.services.llm.interpreter import GoalInterpreter
from backend.memory.memory_manager import MemoryManager
from backend.planner.task_planner import TaskPlanner
from backend.recovery.recovery_engine import RecoveryEngine
from backend.security.action_registry import AllowedActionRegistry
from backend.security.permission_manager import PermissionManager


def test_agent_manager_registration():
    perm_manager = PermissionManager()
    manager = AgentManager(
        goal_agent=GoalAgent(GoalInterpreter(provider=None)),
        planner_agent=PlannerAgent(TaskPlanner(AllowedActionRegistry())),
        file_agent=FileAgent(perm_manager),
        browser_agent=BrowserAgent(),
        application_agent=ApplicationAgent(),
        memory_agent=MemoryAgent(MemoryManager()),
        recovery_agent=RecoveryAgent(RecoveryEngine()),
    )
    assert manager.get("FileAgent").name == "FileAgent"
