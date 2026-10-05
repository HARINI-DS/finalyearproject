from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel


router = APIRouter(prefix="/api/memory", tags=["memory"])


def get_services():
    from backend.main import services

    return services


class PreferenceRequest(BaseModel):
    key: str
    value: str


@router.get("")
def get_memory(svc=Depends(get_services)):
    return {
        "preferences": svc.memory.get_preferences(),
        "history": svc.memory.get_history(),
    }


@router.post("/preferences")
def set_preference(payload: PreferenceRequest, svc=Depends(get_services)):
    svc.memory.set_preference(payload.key, payload.value)
    return {"saved": True, "key": payload.key, "value": payload.value}
