from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.api.goal_routes import router as goal_router
from backend.api.learning_routes import router as learning_router
from backend.api.memory_routes import router as memory_router
from backend.api.system_routes import router as system_router
from backend.api.workflow_routes import router as workflow_router
from backend.core.app_state import build_services
from backend.core.config import settings

app = FastAPI(title="AION")
services = build_services()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goal_router)
app.include_router(workflow_router)
app.include_router(memory_router)
app.include_router(learning_router)
app.include_router(system_router)


@app.websocket("/ws/workflow/{workflow_id}")
async def workflow_socket(websocket: WebSocket, workflow_id: str):
    await websocket.accept()
    queue = services.events.subscribe(workflow_id)

    try:
        while True:
            message = await queue.get()
            await websocket.send_json(message)
    except WebSocketDisconnect:
        services.events.unsubscribe(workflow_id, queue)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=True)
