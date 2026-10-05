from __future__ import annotations

import json
from datetime import datetime
from typing import Iterable

from sqlalchemy import select

from backend.memory.database import SessionLocal
from backend.models.database_models import (
    ExecutionHistoryRecord,
    GoalRecord,
    UserPreferenceRecord,
    WorkflowRecord,
    WorkflowTaskRecord,
)
from backend.models.schemas import ExecutionResult, WorkflowPlan


class MemoryManager:
    def save_workflow_plan(self, plan: WorkflowPlan, original_goal: str) -> int:
        with SessionLocal() as db:
            goal = GoalRecord(text=original_goal, normalized_goal=plan.goal.lower().strip())
            db.add(goal)
            db.flush()

            workflow = WorkflowRecord(goal_id=goal.id, name=plan.goal)
            db.add(workflow)
            db.flush()

            for idx, task in enumerate(plan.tasks):
                db.add(
                    WorkflowTaskRecord(
                        workflow_id=workflow.id,
                        task_id=task.id,
                        action=task.action,
                        agent=task.agent,
                        parameters=json.dumps(task.parameters),
                        ordering=idx,
                    )
                )

            db.commit()
            return workflow.id

    def mark_workflow_approval(self, workflow_id: int, approved: bool) -> None:
        with SessionLocal() as db:
            workflow = db.get(WorkflowRecord, workflow_id)
            if not workflow:
                return
            workflow.approved = approved
            db.commit()

    def record_execution(self, workflow_id: int, action: str, result: ExecutionResult) -> None:
        with SessionLocal() as db:
            workflow = db.get(WorkflowRecord, workflow_id)
            if not workflow:
                return

            db.add(
                ExecutionHistoryRecord(
                    workflow_id=workflow_id,
                    task_id=result.task_id,
                    action=action,
                    agent=result.agent,
                    status=result.status.value,
                    message=result.message,
                    execution_time=result.execution_time,
                    error=result.error,
                )
            )

            workflow.execution_count += 1
            if result.status.value in {"COMPLETED", "RECOVERED"}:
                workflow.success_count += 1
            elif result.status.value == "FAILED":
                workflow.failure_count += 1

            total_time = workflow.avg_execution_time * (workflow.execution_count - 1)
            workflow.avg_execution_time = (total_time + result.execution_time) / max(
                workflow.execution_count, 1
            )
            workflow.last_execution_at = datetime.utcnow()
            workflow.status = result.status.value
            db.commit()

    def get_history(self) -> list[dict]:
        with SessionLocal() as db:
            rows = db.execute(select(WorkflowRecord).order_by(WorkflowRecord.created_at.desc())).scalars()
            return [
                {
                    "id": row.id,
                    "name": row.name,
                    "status": row.status,
                    "execution_count": row.execution_count,
                    "success_count": row.success_count,
                    "failure_count": row.failure_count,
                    "learned": row.learned,
                    "last_execution_at": row.last_execution_at.isoformat()
                    if row.last_execution_at
                    else None,
                }
                for row in rows
            ]

    def get_workflow(self, workflow_id: int) -> dict | None:
        with SessionLocal() as db:
            workflow = db.get(WorkflowRecord, workflow_id)
            if not workflow:
                return None
            return {
                "id": workflow.id,
                "name": workflow.name,
                "status": workflow.status,
                "approved": workflow.approved,
                "tasks": [
                    {
                        "task_id": t.task_id,
                        "action": t.action,
                        "agent": t.agent,
                        "parameters": json.loads(t.parameters),
                        "ordering": t.ordering,
                    }
                    for t in sorted(workflow.tasks, key=lambda x: x.ordering)
                ],
                "executions": [
                    {
                        "task_id": e.task_id,
                        "status": e.status,
                        "message": e.message,
                        "error": e.error,
                        "execution_time": e.execution_time,
                        "created_at": e.created_at.isoformat(),
                    }
                    for e in workflow.executions
                ],
            }

    def set_preference(self, key: str, value: str) -> None:
        with SessionLocal() as db:
            current = db.execute(
                select(UserPreferenceRecord).where(UserPreferenceRecord.key == key)
            ).scalar_one_or_none()
            if current:
                current.value = value
            else:
                db.add(UserPreferenceRecord(key=key, value=value))
            db.commit()

    def get_preferences(self) -> dict[str, str]:
        with SessionLocal() as db:
            rows = db.execute(select(UserPreferenceRecord)).scalars().all()
            return {row.key: row.value for row in rows}

    def mark_learned(self, workflow_id: int, learned: bool = True) -> None:
        with SessionLocal() as db:
            workflow = db.get(WorkflowRecord, workflow_id)
            if workflow:
                workflow.learned = learned
                db.commit()

    def list_learned_workflows(self) -> list[dict]:
        with SessionLocal() as db:
            rows: Iterable[WorkflowRecord] = db.execute(
                select(WorkflowRecord).where(WorkflowRecord.learned.is_(True))
            ).scalars()
            return [
                {
                    "id": row.id,
                    "name": row.name,
                    "execution_count": row.execution_count,
                    "success_rate": (
                        row.success_count / row.execution_count if row.execution_count else 0.0
                    ),
                }
                for row in rows
            ]
