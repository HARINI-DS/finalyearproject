from __future__ import annotations

from pathlib import Path


class RecoveryEngine:
    def recover(self, action: str, parameters: dict, error: str) -> dict:
        if action == "move_file" and "destination" in parameters:
            destination = Path(parameters["destination"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            return {
                "status": "RECOVERED",
                "message": "Created missing destination folder and can retry.",
                "retry": True,
            }

        if action in {"find_files", "list_directory"} and "directory" in parameters:
            directory = Path(parameters["directory"])
            if not directory.exists():
                return {
                    "status": "FAILED",
                    "message": f"Directory not found: {directory}",
                    "retry": False,
                }

        return {
            "status": "FAILED",
            "message": f"Could not recover: {error}",
            "retry": False,
        }
