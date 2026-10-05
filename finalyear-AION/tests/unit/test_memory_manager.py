from backend.memory.database import init_db
from backend.memory.memory_manager import MemoryManager
from backend.models.schemas import TaskModel, WorkflowPlan


def test_memory_manager_save_and_history():
    init_db()
    manager = MemoryManager()
    plan = WorkflowPlan(
        workflow_id="wf_1",
        goal="Test Goal",
        tasks=[TaskModel(id="t1", action="find_files", agent="FileAgent", parameters={"directory": "C:/"})],
        required_capabilities={"file_access": ["C:/"]},
    )
    manager.save_workflow_plan(plan, "Test Goal")
    assert len(manager.get_history()) >= 1
