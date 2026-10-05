import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

# Grant permissions (including DELETE for delete_file action)
scope = str((Path.home() / "Downloads").resolve())
requests.post(
    f"{BASE_URL}/api/permissions/grant",
    json={"capability": "file_access", "scopes": [scope]}
)

# First, create a test folder to delete
print("Creating test folder...")
plan_response = requests.post(
    f"{BASE_URL}/api/workflow/plan",
    json={"goal": "Create a folder called DeleteMe_Test in Downloads"}
)
workflow_id = plan_response.json()['workflow_id']

requests.post(
    f"{BASE_URL}/api/workflow/approve",
    json={"workflow_id": workflow_id, "approved": True}
)

requests.post(
    f"{BASE_URL}/api/workflow/execute",
    json={"workflow_id": workflow_id, "approved": True}
)

test_folder = Path.home() / "Downloads" / "DeleteMe_Test"
print(f"✓ Folder created: {test_folder.exists()}")

# Now test deleting it
print("\nDeleting test folder...")
plan_response = requests.post(
    f"{BASE_URL}/api/workflow/plan",
    json={"goal": "Delete the DeleteMe_Test folder in Downloads"}
)

result = plan_response.json()
workflow_id = result['workflow_id']
print(f"Workflow ID: {workflow_id}")
print(f"Goal: {result['goal']}")
print(f"Tasks: {len(result['tasks'])}")
for task in result['tasks']:
    print(f"  - {task['action']}")

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
print("\nExecution results:")
for result in exec_response.json()['results']:
    print(f"  Task {result['task_id']}: {result['status']}")
    if result.get('error'):
        print(f"    Error: {result['error']}")

# Verify folder is deleted
print(f"\nFolder exists after delete: {test_folder.exists()}")
