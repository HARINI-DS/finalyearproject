from __future__ import annotations

from typing import Any, Optional

from backend.agents.file_agent import FileAgent
from backend.security.permission_manager import PermissionManager


class FileAutomation:
    """Coordinates file operations with permission management."""

    def __init__(self, file_agent: FileAgent, permission_manager: PermissionManager):
        self.file_agent = file_agent
        self.permission_manager = permission_manager

    def get_required_permission(self, action: str, parameters: dict) -> Optional[dict]:
        """Check if an action requires permission."""
        # Extract path from parameters
        path = None
        if "parent" in parameters and action in ["create_folder", "create_file"]:
            path = parameters["parent"]
        elif "source" in parameters:
            path = parameters["source"]
        elif "path" in parameters:
            path = parameters["path"]
        elif "directory" in parameters:
            path = parameters["directory"]

        if path:
            return self.permission_manager.get_required_permission(action, path)
        return None

    def run(self, action: str, parameters: dict) -> dict[str, Any]:
        """Execute a file operation."""
        return self.file_agent.execute(action, parameters)
