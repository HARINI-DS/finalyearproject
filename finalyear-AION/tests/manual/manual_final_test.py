import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

# Grant permissions
scope = str((Path.home() / "Downloads").resolve())
requests.post(
    f"{BASE_URL}/api/permissions/grant",
    json={"capability": "file_access", "scopes": [scope]}
)

# Plan workflow
plan_response = requests.post(
    f"{BASE_URL}/api/workflow/plan",
    json={"goal": "Create a folder called FinalTest_E2E in Downloads"}
)
workflow_id = plan_response.json()['workflow_id']
print(f"Workflow ID: {workflow_id}")

# Approve and execute
requests.post(
    f"{BASE_URL}/api/workflow/approve",
    json={"workflow_id": workflow_id, "approved": True}
)

exec_response = requests.post(
    f"{BASE_URL}/api/workflow/execute",
    json={"workflow_id": workflow_id, "approved": True}
)

# Show results
for result in exec_response.json()['results']:
    print(f"Task {result['task_id']}: {result['status']}")
    if result.get('error'):
        print(f"  Error: {result['error']}")

# Verify folder
test_folder = Path.home() / "Downloads" / "FinalTest_E2E"
print(f"\nFolder exists: {test_folder.exists()}")
