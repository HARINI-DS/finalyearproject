from backend.learning.learning_engine import LearningEngine
from backend.memory.memory_manager import MemoryManager


class FakeMemory(MemoryManager):
    def __init__(self):
        pass

    def get_history(self):
        return [
            {
                "id": 1,
                "name": "Project PDF Organization",
                "execution_count": 5,
                "success_count": 5,
                "failure_count": 0,
                "learned": False,
            }
        ]


def test_learning_candidate_detection():
    engine = LearningEngine(memory=FakeMemory())
    candidates = engine.evaluate_learning_candidates()
    assert len(candidates) == 1
    assert candidates[0]["name"] == "Project PDF Organization"
