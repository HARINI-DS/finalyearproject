from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException

from backend.models.schemas import GoalRequest, WorkflowExecuteRequest


router = APIRouter(prefix="/api/workflow", tags=["workflow"])


def get_services():
    from backend.main import services

    return services


@router.post("/plan")
def plan_workflow(payload: GoalRequest, svc=Depends(get_services)):
    try:
        interpretation = svc.interpreter.interpret(payload.goal)
        plan = svc.planner.create_plan(interpretation.goal, [t.model_dump() for t in interpretation.tasks])
        workflow_db_id = svc.memory.save_workflow_plan(plan, payload.goal)
        svc.plans[plan.workflow_id] = (workflow_db_id, plan)
        return {
            "workflow_id": plan.workflow_id,
            "workflow_db_id": workflow_db_id,
            "goal": plan.goal,
            "tasks": [t.model_dump() for t in plan.tasks],
            "required_capabilities": plan.required_capabilities,
        }
    except Exception as e:
        import traceback
        print(f"ERROR in plan_workflow: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@router.post("/approve")
def approve_workflow(payload: WorkflowExecuteRequest, svc=Depends(get_services)):
    if payload.workflow_id not in svc.plans:
        raise HTTPException(status_code=404, detail="Workflow plan not found")

    workflow_db_id, _ = svc.plans[payload.workflow_id]
    svc.memory.mark_workflow_approval(workflow_db_id, payload.approved)
    return {"workflow_id": payload.workflow_id, "approved": payload.approved}


@router.post("/execute")
async def execute_workflow(payload: WorkflowExecuteRequest, svc=Depends(get_services)):
    if payload.workflow_id not in svc.plans:
        raise HTTPException(status_code=404, detail="Workflow plan not found")
    if not payload.approved:
        raise HTTPException(status_code=400, detail="Approval required")

    workflow_db_id, plan = svc.plans[payload.workflow_id]
    results = await svc.executor.execute_plan(workflow_db_id=workflow_db_id, plan=plan)

    candidates = svc.learning.evaluate_learning_candidates()
    return {
        "workflow_id": payload.workflow_id,
        "results": [r.model_dump() for r in results],
        "learning_candidates": candidates,
    }


@router.get("/history")
def workflow_history(svc=Depends(get_services)):
    return svc.memory.get_history()


@router.get("/{workflow_id}")
def workflow_detail(workflow_id: int, svc=Depends(get_services)):
    item = svc.memory.get_workflow(workflow_id)
    if not item:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return item
