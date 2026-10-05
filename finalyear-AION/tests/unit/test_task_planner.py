from backend.planner.task_planner import TaskPlanner
from backend.security.action_registry import AllowedActionRegistry


def test_task_planner_builds_capabilities():
    planner = TaskPlanner(AllowedActionRegistry())
    plan = planner.create_plan(
        goal="organize",
        tasks=[
            {
                "id": "1",
                "action": "find_files",
                "agent": "FileAgent",
                "parameters": {"directory": "C:/Users/test/Downloads", "extension": ".pdf"},
            }
        ],
    )
    assert "file_access" in plan.required_capabilities
