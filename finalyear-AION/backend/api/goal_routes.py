from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.models.schemas import GoalRequest


router = APIRouter(prefix="/api/goal", tags=["goal"])


def get_services():
    from backend.main import services

    return services


@router.post("/interpret")
def interpret_goal(payload: GoalRequest, svc=Depends(get_services)):
    interpretation = svc.interpreter.interpret(payload.goal)
    return interpretation.model_dump()
