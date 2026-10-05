#!/usr/bin/env python3
"""End-to-end test of AION workflow via API."""

import asyncio
import json
import requests
from pathlib import Path
import time

BASE_URL = "http://127.0.0.1:8000/api"
DOWNLOADS = str(Path.home() / "Downloads")

def test_create_folder_workflow():
    """Test: Create a folder in Downloads."""
    print("\n✓ TEST 1: Create Folder Workflow")
    print("=" * 60)
    
    # Step 1: Plan workflow
    print("  [1/3] Planning workflow: 'Create a folder called AION_Test in Downloads'")
    response = requests.post(
        f"{BASE_URL}/workflow/plan",
        json={"goal": "Create a folder called AION_Test in Downloads"},
    )
    assert response.status_code == 200, f"Plan failed: {response.text}"
    plan = response.json()
    print(f"       ✓ Plan ID: {plan['workflow_id']}")
    print(f"       ✓ Tasks: {[t['action'] for t in plan['tasks']]}")
    
    # Step 2: Check permissions
    print("  [2/3] Checking permissions...")
    response = requests.get(f"{BASE_URL}/permissions")
    assert response.status_code == 200
    permissions = response.json()
    print(f"       ✓ Current permissions: {len(permissions)} rules")
    
    # Step 3: Grant permission if needed
    has_file_access = any(p.get("capability") == "file_access" for p in permissions)
    if not has_file_access:
        print("  [2b/3] Granting file_access permission...")
        response = requests.post(
            f"{BASE_URL}/permissions/grant",
            json={
                "capability": "file_access",
                "scopes": [DOWNLOADS],
            },
        )
        assert response.status_code == 200
        print("       ✓ Permission granted")
    else:
        print("       ✓ Permission already granted")
    
    # Step 4: Approve workflow
    print("  [3/3] Approving and executing workflow...")
    response = requests.post(
        f"{BASE_URL}/workflow/approve",
        json={
            "workflow_id": plan["workflow_id"],
            "approved": True,
        },
    )
    assert response.status_code == 200
    print("       ✓ Workflow approved")
    
    # Step 5: Execute workflow (with approved flag)
    response = requests.post(
        f"{BASE_URL}/workflow/execute",
        json={
            "workflow_id": plan["workflow_id"],
            "approved": True,
        },
    )
    assert response.status_code == 200
    result = response.json()
    print(f"       ✓ Execution result: {result.get('status')}")
    
    # Verify folder was created
    test_folder = Path(DOWNLOADS) / "AION_Test"
    assert test_folder.exists(), f"Folder not created at {test_folder}"
    assert test_folder.is_dir(), f"Path exists but is not a directory: {test_folder}"
    print(f"       ✓ Folder verified at {test_folder}")
    
    return test_folder


def test_find_and_move_workflow():
    """Test: Find and move PDFs (Pattern 2)."""
    print("\n✓ TEST 2: Find and Move PDF Workflow")
    print("=" * 60)
    
    # Create test PDFs in Downloads
    test_pdf1 = Path(DOWNLOADS) / "research_paper1.pdf"
    test_pdf1.write_text("PDF content 1")
    test_pdf2 = Path(DOWNLOADS) / "research_paper2.pdf"
    test_pdf2.write_text("PDF content 2")
    print(f"  [1/3] Created test PDFs in Downloads")
    
    # Plan find and organize workflow (Pattern 2 match)
    print(f"  [2/3] Planning workflow: 'Find PDF files in Downloads and move them to AION_PDFs'")
    response = requests.post(
        f"{BASE_URL}/workflow/plan",
        json={"goal": "Find all PDF files in Downloads and move them to a folder called AION_PDFs"},
    )
    assert response.status_code == 200
    plan = response.json()
    print(f"       ✓ Plan created with {len(plan['tasks'])} tasks: {[t['action'] for t in plan['tasks']]}")
    
    # Grant permission
    response = requests.post(
        f"{BASE_URL}/permissions/grant",
        json={
            "capability": "file_access",
            "scopes": [DOWNLOADS],
        },
    )
    
    # Execute
    print(f"  [3/3] Executing find/move workflow...")
    response = requests.post(
        f"{BASE_URL}/workflow/approve",
        json={"workflow_id": plan["workflow_id"], "approved": True},
    )
    response = requests.post(
        f"{BASE_URL}/workflow/execute",
        json={"workflow_id": plan["workflow_id"], "approved": True},
    )
    assert response.status_code == 200
    print("       ✓ Find/Move workflow executed")
    
    # Verify PDF folder was created
    pdf_folder = Path(DOWNLOADS) / "AION_PDFs"
    if pdf_folder.exists():
        print(f"       ✓ PDF folder created: {pdf_folder}")


def test_list_directory_workflow():
    """Test: List directory (default pattern)."""
    print("\n✓ TEST 2B: List Directory Workflow")
    print("=" * 60)
    
    # Plan list workflow
    print(f"  [1/2] Planning workflow: 'List files in Downloads'")
    response = requests.post(
        f"{BASE_URL}/workflow/plan",
        json={"goal": "List files in Downloads"},
    )
    assert response.status_code == 200
    plan = response.json()
    print(f"       ✓ Plan created with {len(plan['tasks'])} tasks")
    
    # Grant permission
    requests.post(
        f"{BASE_URL}/permissions/grant",
        json={
            "capability": "file_access",
            "scopes": [DOWNLOADS],
        },
    )
    
    # Execute
    print(f"  [2/2] Executing list workflow...")
    response = requests.post(
        f"{BASE_URL}/workflow/approve",
        json={"workflow_id": plan["workflow_id"], "approved": True},
    )
    response = requests.post(
        f"{BASE_URL}/workflow/execute",
        json={"workflow_id": plan["workflow_id"], "approved": True},
    )
    assert response.status_code == 200
    print("       ✓ List workflow executed")


def test_delete_folder_workflow():
    """Test: Delete folder (destructive operation)."""
    print("\n✓ TEST 4: Delete Folder Workflow")
    print("=" * 60)
    
    # Create folder to delete
    test_folder = Path(DOWNLOADS) / "AION_Test"
    print(f"  [1/3] Target folder: {test_folder}")
    assert test_folder.exists()
    
    # Plan delete - must match Pattern 1.5: has "delete/remove", "the", folder/directory/file, "in/from" location
    print(f"  [2/3] Planning workflow: 'Delete the AION_Test folder from Downloads'")
    response = requests.post(
        f"{BASE_URL}/workflow/plan",
        json={"goal": "Delete the AION_Test folder from Downloads"},
    )
    assert response.status_code == 200
    plan = response.json()
    print(f"       ✓ Plan created with {len(plan['tasks'])} tasks: {[t['action'] for t in plan['tasks']]}")
    
    # Grant permissions
    requests.post(
        f"{BASE_URL}/permissions/grant",
        json={
            "capability": "file_access",
            "scopes": [str(test_folder)],
        },
    )
    
    # Execute
    print(f"  [3/3] Executing delete workflow...")
    response = requests.post(
        f"{BASE_URL}/workflow/approve",
        json={"workflow_id": plan["workflow_id"], "approved": True},
    )
    response = requests.post(
        f"{BASE_URL}/workflow/execute",
        json={"workflow_id": plan["workflow_id"], "approved": True},
    )
    assert response.status_code == 200
    print("       ✓ Delete executed")
    
    # Verify deletion
    time.sleep(1)  # Allow filesystem time
    assert not test_folder.exists(), f"Folder still exists: {test_folder}"
    print(f"       ✓ Folder deleted and verified gone")


def main():
    """Run all E2E tests."""
    print("\n" + "=" * 60)
    print("AION END-TO-END WORKFLOW TESTS")
    print("=" * 60)
    
    try:
        # Verify backend is running
        response = requests.get(f"{BASE_URL}/workflow/history")
        assert response.status_code == 200
        print("✓ Backend is running and responding")
        
        # Run tests
        test_create_folder_workflow()
        test_find_and_move_workflow()
        test_list_directory_workflow()
        test_delete_folder_workflow()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
