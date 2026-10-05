from __future__ import annotations

from datetime import datetime
from pathlib import Path
import platform
import psutil


class ContextEngine:
    def collect(self) -> dict:
        running_apps = [p.info["name"] for p in psutil.process_iter(["name"]) if p.info.get("name")]
        return {
            "os": platform.platform(),
            "cwd": str(Path.cwd()),
            "time": datetime.now().isoformat(),
            "running_applications": sorted(set(running_apps))[:40],
        }
