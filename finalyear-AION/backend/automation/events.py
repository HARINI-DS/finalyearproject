from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = defaultdict(list)

    async def publish(self, workflow_id: str, payload: dict[str, Any]) -> None:
        for queue in self._queues[workflow_id]:
            await queue.put(payload)

    def subscribe(self, workflow_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._queues[workflow_id].append(queue)
        return queue

    def unsubscribe(self, workflow_id: str, queue: asyncio.Queue) -> None:
        if workflow_id in self._queues and queue in self._queues[workflow_id]:
            self._queues[workflow_id].remove(queue)
