import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Use Python 3.11 to run this test
# Grant permissions
scope = str((__import__("pathlib").Path.home() / "Downloads").resolve())
print(f"Granting permissions for scope: {scope}")
requests.post(
    f"{BASE_URL}/api/permissions/grant",
    json={"capability": "file_access", "scopes": [scope]}
)

# First, create a test folder to delete
print("\nCreating test folder...")
plan_response = requests.post(
    f"{BASE_URL}/api/workflow/plan",
    json={"goal": "Create a folder called DeleteMe_Test in Downloads"}
)

workflow_id = plan_response.json()['workflow_id']
print(f"✓ Workflow created: {workflow_id}")
print(f"  Plan: {[t.get('action') for t in plan_response.json()['tasks']]}")

requests.post(
    f"{BASE_URL}/api/workflow/approve",
    json={"workflow_id": workflow_id, "approved": True}
)

exec_resp = requests.post(
    f"{BASE_URL}/api/workflow/execute",
    json={"workflow_id": workflow_id, "approved": True}
)

test_folder = (__import__("pathlib").Path.home() / "Downloads" / "DeleteMe_Test")
print(f"✓ Folder created: {test_folder.exists()}")

# Now test deleting it
print("\nDeleting test folder...")
plan_response = requests.post(
    f"{BASE_URL}/api/workflow/plan",
    json={"goal": "Delete the DeleteMe_Test folder in Downloads"}
)

print(f"Response status: {plan_response.status_code}")
if plan_response.status_code == 200:
    result = plan_response.json()
    print(f"\n✓ Plan Result:")
    print(f"  Goal: {result['goal']}")
    print(f"  Tasks: {[t.get('action') for t in result['tasks']]}")
    
    workflow_id = result['workflow_id']
    
    # Approve
    print(f"\nApproving workflow...")
    requests.post(
        f"{BASE_URL}/api/workflow/approve",
        json={"workflow_id": workflow_id, "approved": True}
    )
    
    # Execute
    print(f"Executing workflow...")
    exec_response = requests.post(
        f"{BASE_URL}/api/workflow/execute",
        json={"workflow_id": workflow_id, "approved": True}
    )
    
    if exec_response.status_code == 200:
        exec_result = exec_response.json()
        print(f"✓ Execution Result:")
        print(f"  Workflow ID: {exec_result.get('workflow_id')}")
        print(f"  Results: {exec_result.get('results')}")
        print(f"\n  Folder still exists: {test_folder.exists()}")
        if not test_folder.exists():
            print("  ✓✓✓ DELETE WORKFLOW SUCCESSFUL! ✓✓✓")
    else:
        print(f"✗ Execute status: {exec_response.status_code}")
        print(f"  Text: {exec_response.text[:500]}")
else:
    print(f"✗ Plan failed: {plan_response.text[:500]}")
