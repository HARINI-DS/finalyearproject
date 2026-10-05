from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(prefix="/api/learning", tags=["learning"])


def get_services():
    from backend.main import services

    return services


@router.get("/workflows")
def list_learned(svc=Depends(get_services)):
    return svc.learning.list_learned()


@router.post("/{workflow_id}/run")
def run_learned(workflow_id: int, svc=Depends(get_services)):
    detail = svc.memory.get_workflow(workflow_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"workflow": detail, "message": "Use /api/workflow/execute after approval"}


@router.post("/{workflow_id}/save")
def save_learned(workflow_id: int, svc=Depends(get_services)):
    svc.learning.save_as_learned_workflow(workflow_id)
    return {"workflow_id": workflow_id, "learned": True}
