from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.recovery.recovery_engine import RecoveryEngine


class RecoveryAgent(BaseAgent):
    name = "RecoveryAgent"

    def __init__(self, recovery: RecoveryEngine) -> None:
        self.recovery = recovery

    def recover_failure(self, action: str, parameters: dict[str, Any], error: str) -> dict[str, Any]:
        return self.recovery.recover(action=action, parameters=parameters, error=error)

    def execute(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if action != "recover_failure":
            raise ValueError(f"Unsupported action: {action}")
        return self.recover_failure(**parameters)
