#!/usr/bin/env python3
import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

# Step 0: Grant permissions
print("Step 0: Granting permissions...")
grant_response = requests.post(
    f"{BASE_URL}/api/permissions/grant",
    json={
        "capability": "file_access",
        "scopes": ["C:\\Users\\jayas\\Downloads"]
    }
)
print(f"✓ Permissions granted")

# Step 1: Plan the workflow
print("\nStep 1: Planning workflow...")
plan_response = requests.post(
    f"{BASE_URL}/api/workflow/plan",
    json={"goal": "Create a folder called BackendTest_E2E in Downloads"}
)
plan_data = plan_response.json()
workflow_id = plan_data['workflow_id']
print(f"✓ Workflow planned. ID: {workflow_id}")
print(f"  Goal: {plan_data['goal']}")
print(f"  Tasks: {len(plan_data['tasks'])}")
for task in plan_data['tasks']:
    print(f"    - {task['action']} via {task['agent']}")

# Step 2: Approve the workflow
print("\nStep 2: Approving workflow...")
approve_response = requests.post(
    f"{BASE_URL}/api/workflow/approve",
    json={"workflow_id": workflow_id, "approved": True}
)
print(f"✓ Workflow approved")

# Step 3: Execute the workflow
print("\nStep 3: Executing workflow...")
exec_response = requests.post(
    f"{BASE_URL}/api/workflow/execute",
    json={"workflow_id": workflow_id, "approved": True}
)
exec_data = exec_response.json()
print(f"✓ Workflow executed")
print(f"  Status: {exec_data.get('status', 'unknown')}")
if 'results' in exec_data:
    for result in exec_data['results']:
        print(f"  Task {result['task_id']}: {result['status']}")
        if result['status'] != 'SUCCESS':
            print(f"    Error: {result.get('error', 'unknown')}")

# Step 4: Verify the folder was created
print("\nStep 4: Verifying folder creation...")
home = Path.home()
downloads = home / "Downloads"
test_folder = downloads / "BackendTest_E2E"

if test_folder.exists():
    print(f"✓ Folder created successfully at: {test_folder}")
    print(f"  Is directory: {test_folder.is_dir()}")
else:
    print(f"✗ Folder NOT found at: {test_folder}")
    backend_folders = list(downloads.glob('*Backend*'))
    print(f"  Folders matching 'Backend*': {backend_folders}")

print("\n" + "="*60)
print("END-TO-END WORKFLOW TEST COMPLETE")
print("="*60)
