from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException

from backend.models.schemas import PermissionGrantRequest


router = APIRouter(prefix="/api", tags=["system"])


def get_services():
    from backend.main import services

    return services


@router.get("/health")
def health():
    return {"status": "ok", "service": "AION"}


@router.get("/system/context")
def get_context(svc=Depends(get_services)):
    return svc.context.collect()


# PERMISSION ENDPOINTS

@router.get("/permissions")
def get_permissions(svc=Depends(get_services)):
    """Get all current permissions."""
    return svc.permissions.get_permissions()


@router.post("/permissions/request")
def request_permissions(
    action: str, path: str, svc=Depends(get_services)
):
    """
    Check if an action requires permission.
    
    Returns:
    - null if permission is already granted
    - permission request object if permission is needed
    """
    required = svc.permissions.get_required_permission(action, path)
    if required:
        return {
            "status": "PERMISSION_REQUIRED",
            "requirement": required,
        }
    return {"status": "PERMISSION_GRANTED"}


@router.post("/permissions/grant")
def grant_permissions(payload: PermissionGrantRequest, svc=Depends(get_services)):
    """Grant permissions for given scopes."""
    return svc.permissions.grant(payload.capability, payload.scopes)


@router.post("/permissions/revoke")
def revoke_permissions(payload: PermissionGrantRequest, svc=Depends(get_services)):
    """Revoke permissions for given scopes."""
    return svc.permissions.revoke(payload.capability, payload.scopes)


# FILE OPERATION ENDPOINTS

@router.post("/file/create-folder")
def create_folder(parent: str, name: str, svc=Depends(get_services)):
    """
    Create a folder.
    
    Requires WRITE permission on parent directory.
    """
    file_agent = svc.executor.agent_manager.get("FileAgent")
    result = file_agent.create_folder(parent, name)
    return result


@router.post("/file/create-file")
def create_file(parent: str, name: str, content: str = "", svc=Depends(get_services)):
    """
    Create a file.
    
    Requires WRITE permission on parent directory.
    """
    file_agent = svc.executor.agent_manager.get("FileAgent")
    result = file_agent.create_file(parent, name, content)
    return result


@router.post("/file/rename")
def rename_item(source: str, new_name: str, svc=Depends(get_services)):
    """
    Rename a file or folder.
    
    Requires WRITE permission on the containing directory.
    """
    file_agent = svc.executor.agent_manager.get("FileAgent")
    result = file_agent.rename_item(source, new_name)
    return result


@router.post("/file/move")
def move_item(source: str, destination: str, svc=Depends(get_services)):
    """
    Move a file or folder.
    
    Requires WRITE permission on both source and destination directories.
    """
    file_agent = svc.executor.agent_manager.get("FileAgent")
    result = file_agent.move_item(source, destination)
    return result


@router.post("/file/combine")
def combine_files(files: list[str], destination_directory: str, output_name: str | None = None, svc=Depends(get_services)):
    """Combine multiple PDFs into a single file."""
    file_agent = svc.executor.agent_manager.get("FileAgent")
    return file_agent.combine_files(files, destination_directory, output_name)


@router.post("/file/copy")
def copy_item(source: str, destination: str, svc=Depends(get_services)):
    """
    Copy a file or folder.
    
    Requires READ on source and WRITE on destination.
    """
    file_agent = svc.executor.agent_manager.get("FileAgent")
    result = file_agent.copy_item(source, destination)
    return result


@router.delete("/file")
def delete_item(path: str, svc=Depends(get_services)):
    """
    Delete a file or folder.
    
    Requires DELETE permission.
    This is a high-risk operation that always requires explicit confirmation.
    """
    file_agent = svc.executor.agent_manager.get("FileAgent")
    result = file_agent.delete_item(path)
    return result


@router.get("/file/list")
def list_directory(path: str, svc=Depends(get_services)):
    """
    List directory contents.
    
    Requires READ permission.
    """
    file_agent = svc.executor.agent_manager.get("FileAgent")
    result = file_agent.list_directory(path)
    return result


@router.get("/file/find")
def find_files(path: str, pattern: Optional[str] = None, svc=Depends(get_services)):
    """
    Find files matching a pattern.
    
    Requires READ permission.
    Pattern can be: "pdf", "*.txt", "exp*.pdf", etc.
    """
    file_agent = svc.executor.agent_manager.get("FileAgent")
    result = file_agent.find_files(path, pattern)
    return result


@router.post("/file/open-explorer")
def open_in_explorer(path: str, svc=Depends(get_services)):
    """
    Open a path in Windows File Explorer.
    
    Requires READ permission.
    """
    file_agent = svc.executor.agent_manager.get("FileAgent")
    result = file_agent.open_in_explorer(path)
    return result


@router.get("/file/exists")
def file_exists(path: str, svc=Depends(get_services)):
    """
    Check if a file or folder exists.
    
    Requires READ permission.
    """
    file_agent = svc.executor.agent_manager.get("FileAgent")
    result = file_agent.exists(path)
    return result
