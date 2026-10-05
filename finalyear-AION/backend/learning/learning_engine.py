from __future__ import annotations

from backend.memory.memory_manager import MemoryManager


class LearningEngine:
    def __init__(self, memory: MemoryManager, learn_threshold: int = 5) -> None:
        self.memory = memory
        self.learn_threshold = learn_threshold

    def evaluate_learning_candidates(self) -> list[dict]:
        candidates: list[dict] = []
        for workflow in self.memory.get_history():
            if workflow["execution_count"] < self.learn_threshold:
                continue
            if workflow["failure_count"] > 0:
                continue

            success_rate = (
                workflow["success_count"] / workflow["execution_count"]
                if workflow["execution_count"]
                else 0.0
            )
            if success_rate >= 0.9 and not workflow.get("learned", False):
                candidates.append(
                    {
                        "id": workflow["id"],
                        "name": workflow["name"],
                        "execution_count": workflow["execution_count"],
                        "success_rate": success_rate,
                        "message": "I noticed you frequently perform this task.",
                    }
                )
        return candidates

    def save_as_learned_workflow(self, workflow_id: int) -> None:
        self.memory.mark_learned(workflow_id, True)

    def list_learned(self) -> list[dict]:
        return self.memory.list_learned_workflows()
