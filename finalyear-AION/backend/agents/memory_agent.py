from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.memory.memory_manager import MemoryManager


class MemoryAgent(BaseAgent):
    name = "MemoryAgent"

    def __init__(self, memory: MemoryManager) -> None:
        self.memory = memory

    def save_workflow(self, workflow_id: int, learned: bool = False) -> dict[str, Any]:
        if learned:
            self.memory.mark_learned(workflow_id, True)
        return {"workflow_id": workflow_id, "saved": True, "learned": learned}

    def execute(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if action != "save_workflow":
            raise ValueError(f"Unsupported action: {action}")
        return self.save_workflow(**parameters)
