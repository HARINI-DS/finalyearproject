import requests

BASE_URL = "http://127.0.0.1:8000"

# Grant permissions
scope = str((__import__("pathlib").Path.home() / "Downloads").resolve())
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

test_folder = (__import__("pathlib").Path.home() / "Downloads" / "DeleteMe_Test")
print(f"✓ Folder created: {test_folder.exists()}")

# Now test deleting it
print("\nDeleting test folder...")
plan_response = requests.post(
    f"{BASE_URL}/api/workflow/plan",
    json={"goal": "Delete the DeleteMe_Test folder in Downloads"}
)

print(f"Response status: {plan_response.status_code}")
print(f"Response text: {plan_response.text}")

if plan_response.status_code == 200:
    result = plan_response.json()
    print(f"Result: {result}")
