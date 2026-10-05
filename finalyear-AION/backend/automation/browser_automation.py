from __future__ import annotations

from backend.agents.browser_agent import BrowserAgent


class BrowserAutomation:
    def __init__(self, browser_agent: BrowserAgent) -> None:
        self.browser_agent = browser_agent

    def run(self, action: str, parameters: dict):
        return self.browser_agent.execute(action, parameters)
