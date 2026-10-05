from __future__ import annotations

from backend.agents.application_agent import ApplicationAgent
from backend.agents.browser_agent import BrowserAgent
from backend.agents.file_agent import FileAgent
from backend.agents.goal_agent import GoalAgent
from backend.agents.memory_agent import MemoryAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.recovery_agent import RecoveryAgent


class AgentManager:
    def __init__(
        self,
        goal_agent: GoalAgent,
        planner_agent: PlannerAgent,
        file_agent: FileAgent,
        browser_agent: BrowserAgent,
        application_agent: ApplicationAgent,
        memory_agent: MemoryAgent,
        recovery_agent: RecoveryAgent,
    ) -> None:
        self.agents = {
            goal_agent.name: goal_agent,
            planner_agent.name: planner_agent,
            file_agent.name: file_agent,
            browser_agent.name: browser_agent,
            application_agent.name: application_agent,
            memory_agent.name: memory_agent,
            recovery_agent.name: recovery_agent,
        }

    def get(self, name: str):
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' is not registered")
        return self.agents[name]
