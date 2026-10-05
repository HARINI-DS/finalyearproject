import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

# Step 1: Check current permissions
print("Step 1: Checking current permissions...")
perm_response = requests.get(f"{BASE_URL}/api/permissions")
perms = perm_response.json()
print(f"  Current permissions: {json.dumps(perms, indent=2)}")

# Step 2: Grant permissions again to be sure
print("\nStep 2: Granting permissions...")
scope = str((Path.home() / "Downloads").resolve())
print(f"  Granting for scope: {scope}")
grant_response = requests.post(
    f"{BASE_URL}/api/permissions/grant",
    json={
        "capability": "file_access",
        "scopes": [scope]
    }
)
print(f"  Grant response: {grant_response.json()}")

# Step 3: Check permissions again
print("\nStep 3: Checking permissions after grant...")
perm_response = requests.get(f"{BASE_URL}/api/permissions")
perms = perm_response.json()
print(f"  Permissions: {json.dumps(perms, indent=2)}")

# Step 4: Plan workflow
print("\nStep 4: Planning workflow...")
plan_response = requests.post(
    f"{BASE_URL}/api/workflow/plan",
    json={"goal": "Create a folder called DebugTest in Downloads"}
)
plan_data = plan_response.json()
workflow_id = plan_data['workflow_id']
print(f"✓ Workflow ID: {workflow_id}")
print(f"  Goal: {plan_data['goal']}")
print(f"  Tasks: {len(plan_data['tasks'])}")

# Step 5: Approve and execute
print("\nStep 5: Approving and executing...")
approve_response = requests.post(
    f"{BASE_URL}/api/workflow/approve",
    json={"workflow_id": workflow_id, "approved": True}
)

exec_response = requests.post(
    f"{BASE_URL}/api/workflow/execute",
    json={"workflow_id": workflow_id, "approved": True}
)
exec_data = exec_response.json()
print(f"  Results:")
for result in exec_data.get('results', []):
    print(f"    Task {result['task_id']}: {result['status']}")
    if result.get('error'):
        print(f"      Error: {result['error']}")
