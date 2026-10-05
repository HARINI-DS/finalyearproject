from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.automation.file_operations import FileOperations
from backend.automation.path_validator import PathValidator
from backend.security.permission_manager import PermissionManager


class FileAgent(BaseAgent):
    """Agent for real Windows filesystem operations with permission control."""

    name = "FileAgent"

    def __init__(self, permission_manager: PermissionManager):
        self.permission_manager = permission_manager
        self.file_ops = FileOperations()

    # WRITE operations (require permission and confirmation)

    def create_folder(self, parent: str, name: str) -> dict[str, Any]:
        """Create a folder."""
        return self.file_ops.create_folder(parent, name).model_dump()

    def create_file(self, parent: str, name: str, content: str = "") -> dict[str, Any]:
        """Create a file."""
        return self.file_ops.create_file(parent, name, content).model_dump()

    def rename_item(self, source: str, new_name: str) -> dict[str, Any]:
        """Rename a file or folder."""
        return self.file_ops.rename_item(source, new_name).model_dump()

    def move_item(self, source: str, destination: str) -> dict[str, Any]:
        """Move a file or folder."""
        return self.file_ops.move_item(source, destination).model_dump()

    def move_files(self, files: list[str], destination_directory: str) -> dict[str, Any]:
        """Move multiple files to a directory."""
        results = []
        for file_path in files:
            result = self.file_ops.move_item(file_path, destination_directory)
            results.append(result.model_dump())

        return {
            "action": "move_files",
            "status": "COMPLETED" if all(r["status"] == "COMPLETED" for r in results) else "PARTIAL",
            "results": results,
            "count": len([r for r in results if r["status"] == "COMPLETED"]),
        }

    def combine_files(self, files: list[str], destination_directory: str, output_name: str | None = None) -> dict[str, Any]:
        """Combine multiple PDF files into a single output file."""
        return self.file_ops.combine_files(files, destination_directory, output_name).model_dump()

    def copy_item(self, source: str, destination: str) -> dict[str, Any]:
        """Copy a file or folder."""
        return self.file_ops.copy_item(source, destination).model_dump()

    def delete_item(self, path: str) -> dict[str, Any]:
        """Delete a file or folder."""
        return self.file_ops.delete_item(path).model_dump()

    # READ operations (may require permission to access directory)

    def list_directory(self, directory: str) -> dict[str, Any]:
        """List directory contents."""
        return self.file_ops.list_directory(directory).model_dump()

    def find_files(self, directory: str, pattern: str = None) -> dict[str, Any]:
        """Find files matching a pattern."""
        return self.file_ops.find_files(directory, pattern).model_dump()

    def open_in_explorer(self, path: str) -> dict[str, Any]:
        """Open path in Windows File Explorer."""
        return self.file_ops.open_in_explorer(path).model_dump()

    def exists(self, path: str) -> dict[str, Any]:
        """Check if path exists."""
        return self.file_ops.exists(path).model_dump()

    # Legacy compatibility methods
    def rename_file(self, source: str, new_name: str) -> dict[str, Any]:
        """Legacy: rename a file."""
        return self.rename_item(source, new_name)

    def delete_file(self, source: str) -> dict[str, Any]:
        """Legacy: delete a file."""
        return self.delete_item(source)

    def move_file(self, source: str, destination: str) -> dict[str, Any]:
        """Legacy: move a file."""
        return self.move_item(source, destination)

    def copy_file(self, source: str, destination: str) -> dict[str, Any]:
        """Legacy: copy a file."""
        return self.copy_item(source, destination)

    def verify_file(self, path: str) -> dict[str, Any]:
        """Legacy: verify a file exists."""
        return self.exists(path)

    def verify_folder(self, path: str) -> dict[str, Any]:
        """Legacy: verify a folder exists."""
        return self.exists(path)

    def verify(self, path: str) -> dict[str, Any]:
        """Legacy: verify a path exists."""
        return self.exists(path)

    def execute(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute an action."""
        if not hasattr(self, action):
            raise ValueError(f"Unsupported action: {action}")
        method = getattr(self, action)
        return method(**parameters)
