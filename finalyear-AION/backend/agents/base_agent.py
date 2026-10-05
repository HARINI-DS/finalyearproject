from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def execute(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
