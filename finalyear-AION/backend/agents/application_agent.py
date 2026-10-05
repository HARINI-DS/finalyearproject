from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any

from backend.agents.base_agent import BaseAgent


class ApplicationAgent(BaseAgent):
    name = "ApplicationAgent"

    APP_MAP = {
        "chrome": ["chrome", "chrome.exe"],
        "vs code": ["code", "code.cmd"],
        "notepad": ["notepad.exe"],
        "powerpoint": ["POWERPNT.EXE"],
        "file explorer": ["explorer.exe"],
    }

    def open_application(self, name: str) -> dict[str, Any]:
        normalized = name.lower().strip()
        candidates = self.APP_MAP.get(normalized, [name])

        for candidate in candidates:
            path = shutil.which(candidate)
            if path:
                subprocess.Popen([path], shell=False)
                return {"opened": name, "path": path}

        if normalized == "file explorer":
            os.startfile("explorer.exe")
            return {"opened": name, "path": "explorer.exe"}

        raise FileNotFoundError(f"{name} was not found on this computer.")

    def execute(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if action != "open_application":
            raise ValueError(f"Unsupported action: {action}")
        return self.open_application(**parameters)
