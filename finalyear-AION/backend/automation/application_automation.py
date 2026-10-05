from __future__ import annotations

from backend.agents.application_agent import ApplicationAgent


class ApplicationAutomation:
    def __init__(self, app_agent: ApplicationAgent) -> None:
        self.app_agent = app_agent

    def run(self, action: str, parameters: dict):
        return self.app_agent.execute(action, parameters)
