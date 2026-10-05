from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RECOVERED = "RECOVERED"
    CANCELLED = "CANCELLED"


class TaskModel(BaseModel):
    id: str
    action: str
    agent: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    requires_confirmation: bool = False


class GoalInterpretation(BaseModel):
    goal: str
    tasks: List[TaskModel]


class WorkflowPlan(BaseModel):
    workflow_id: str
    goal: str
    tasks: List[TaskModel]
    required_capabilities: Dict[str, List[str]]


class ExecutionResult(BaseModel):
    task_id: str
    status: ExecutionStatus
    agent: str
    message: str
    execution_time: float
    error: Optional[str] = None
    recovery: Optional[Dict[str, Any]] = None


class GoalRequest(BaseModel):
    goal: str


class WorkflowExecuteRequest(BaseModel):
    workflow_id: str
    approved: bool = False


class PermissionGrantRequest(BaseModel):
    capability: str
    scopes: List[str]
    mode: str = "grant"
