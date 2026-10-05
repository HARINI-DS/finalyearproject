"""Real Windows filesystem operations with verification."""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from backend.automation.path_validator import PathValidator


class FileOperationResult:
    """Structured result of a filesystem operation."""

    def __init__(
        self,
        action: str,
        status: str,
        path: Optional[str] = None,
        message: str = "",
        verified: bool = False,
        error: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        self.action = action
        self.status = status
        self.path = path
        self.message = message
        self.verified = verified
        self.error = error
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()

    def model_dump(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "action": self.action,
            "status": self.status,
            "path": self.path,
            "message": self.message,
            "verified": self.verified,
            "error": self.error,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class FileOperations:
    """Real Windows filesystem operations with verification."""

    @staticmethod
    def create_folder(parent: str, name: str) -> FileOperationResult:
        """Create a folder with verification."""
        try:
            parent_path = PathValidator.validate_write_path(parent)
            target_path = parent_path / name

            # Check for conflicts
            if target_path.exists():
                return FileOperationResult(
                    action="create_folder",
                    status="FAILED",
                    path=PathValidator.normalize_path(target_path),
                    error=f"Folder already exists: {name}",
                    details={"conflict": True},
                )

            # Create folder
            target_path.mkdir(parents=True, exist_ok=True)

            # Verify creation
            if not target_path.exists() or not target_path.is_dir():
                return FileOperationResult(
                    action="create_folder",
                    status="FAILED",
                    path=PathValidator.normalize_path(target_path),
                    error="Verification failed: folder was not created",
                    verified=False,
                )

            return FileOperationResult(
                action="create_folder",
                status="COMPLETED",
                path=PathValidator.normalize_path(target_path),
                message=f"Folder '{name}' created successfully.",
                verified=True,
                details={"name": name},
            )

        except Exception as e:
            return FileOperationResult(
                action="create_folder",
                status="FAILED",
                error=str(e),
                details={"parent": parent, "name": name},
            )

    @staticmethod
    def create_file(parent: str, name: str, content: str = "") -> FileOperationResult:
        """Create a file with verification."""
        try:
            parent_path = PathValidator.validate_write_path(parent)
            target_path = parent_path / name

            # Check for conflicts
            if target_path.exists():
                return FileOperationResult(
                    action="create_file",
                    status="FAILED",
                    path=PathValidator.normalize_path(target_path),
                    error=f"File already exists: {name}",
                    details={"conflict": True},
                )

            # Create file
            target_path.write_text(content, encoding="utf-8")

            # Verify creation
            if not target_path.exists() or not target_path.is_file():
                return FileOperationResult(
                    action="create_file",
                    status="FAILED",
                    path=PathValidator.normalize_path(target_path),
                    error="Verification failed: file was not created",
                    verified=False,
                )

            return FileOperationResult(
                action="create_file",
                status="COMPLETED",
                path=PathValidator.normalize_path(target_path),
                message=f"File '{name}' created successfully.",
                verified=True,
                details={"name": name, "size": len(content)},
            )

        except Exception as e:
            return FileOperationResult(
                action="create_file",
                status="FAILED",
                error=str(e),
                details={"parent": parent, "name": name},
            )

    @staticmethod
    def rename_item(source: str, new_name: str) -> FileOperationResult:
        """Rename a file or folder with verification."""
        try:
            source_path = PathValidator.validate_write_path(source)

            if not source_path.exists():
                return FileOperationResult(
                    action="rename_item",
                    status="FAILED",
                    path=PathValidator.normalize_path(source_path),
                    error=f"Item not found: {source}",
                )

            dest_path = source_path.parent / new_name

            # Check for conflicts
            if dest_path.exists():
                return FileOperationResult(
                    action="rename_item",
                    status="FAILED",
                    path=PathValidator.normalize_path(source_path),
                    error=f"Item already exists: {new_name}",
                    details={"conflict": True},
                )

            # Rename
            source_path.rename(dest_path)

            # Verify
            source_exists = source_path.exists()
            dest_exists = dest_path.exists()

            if source_exists or not dest_exists:
                return FileOperationResult(
                    action="rename_item",
                    status="FAILED",
                    error="Verification failed: rename did not complete properly",
                    verified=False,
                )

            item_type = "folder" if dest_path.is_dir() else "file"
            return FileOperationResult(
                action="rename_item",
                status="COMPLETED",
                path=PathValidator.normalize_path(dest_path),
                message=f"{item_type.capitalize()} renamed to '{new_name}'.",
                verified=True,
                details={"old_name": source_path.name, "new_name": new_name},
            )

        except Exception as e:
            return FileOperationResult(
                action="rename_item",
                status="FAILED",
                error=str(e),
                details={"source": source, "new_name": new_name},
            )

    @staticmethod
    def move_item(source: str, destination: str) -> FileOperationResult:
        """Move a file or folder with verification."""
        try:
            source_path = PathValidator.validate_write_path(source)
            dest_path = PathValidator.validate_write_path(destination)

            if not source_path.exists():
                return FileOperationResult(
                    action="move_item",
                    status="FAILED",
                    error=f"Source not found: {source}",
                )

            # If destination is a directory, move into it
            if dest_path.is_dir():
                final_dest = dest_path / source_path.name
            else:
                final_dest = dest_path

            # Check for conflicts
            if final_dest.exists() and final_dest != source_path:
                return FileOperationResult(
                    action="move_item",
                    status="FAILED",
                    error=f"Destination already exists: {final_dest.name}",
                    details={"conflict": True},
                )

            # Ensure destination directory exists
            final_dest.parent.mkdir(parents=True, exist_ok=True)

            # Move
            shutil.move(str(source_path), str(final_dest))

            # Verify
            if source_path.exists():
                return FileOperationResult(
                    action="move_item",
                    status="FAILED",
                    error="Verification failed: source still exists after move",
                    verified=False,
                )

            if not final_dest.exists():
                return FileOperationResult(
                    action="move_item",
                    status="FAILED",
                    error="Verification failed: destination does not exist",
                    verified=False,
                )

            return FileOperationResult(
                action="move_item",
                status="COMPLETED",
                path=PathValidator.normalize_path(final_dest),
                message=f"Item moved to {PathValidator.get_relative_display_path(final_dest)}",
                verified=True,
                details={"source": PathValidator.normalize_path(source_path)},
            )

        except Exception as e:
            return FileOperationResult(
                action="move_item",
                status="FAILED",
                error=str(e),
                details={"source": source, "destination": destination},
            )

    @staticmethod
    def combine_files(files: list[str], destination_directory: str, output_name: str | None = None) -> FileOperationResult:
        """Combine multiple PDF files into one PDF and verify the result."""
        try:
            if not files:
                return FileOperationResult(
                    action="combine_files",
                    status="FAILED",
                    error="No files provided to combine",
                )

            resolved_files = []
            for file_path in files:
                resolved = PathValidator.validate_read_path(file_path)
                if not resolved.exists():
                    return FileOperationResult(
                        action="combine_files",
                        status="FAILED",
                        error=f"File not found: {file_path}",
                    )
                if resolved.suffix.lower() != ".pdf":
                    return FileOperationResult(
                        action="combine_files",
                        status="FAILED",
                        error=f"Unsupported file type for combination: {resolved.name}",
                        details={"file": str(resolved)},
                    )
                resolved_files.append(resolved)

            output_name = output_name or "combined.pdf"
            if not output_name.lower().endswith(".pdf"):
                output_name = f"{output_name}.pdf"

            destination_path = PathValidator.validate_write_path(destination_directory)
            destination_path.mkdir(parents=True, exist_ok=True)
            output_file = destination_path / output_name

            if output_file.exists():
                return FileOperationResult(
                    action="combine_files",
                    status="FAILED",
                    error=f"Output file already exists: {output_name}",
                    details={"path": str(output_file)},
                )

            try:
                from pypdf import PdfReader, PdfWriter
            except ImportError:
                try:
                    from PyPDF2 import PdfReader, PdfWriter
                except ImportError:
                    return FileOperationResult(
                        action="combine_files",
                        status="FAILED",
                        error="PDF combination requires pypdf or PyPDF2 to be installed.",
                    )

            writer = PdfWriter()
            for pdf_file in resolved_files:
                reader = PdfReader(str(pdf_file))
                for page in reader.pages:
                    writer.add_page(page)

            with output_file.open("wb") as target:
                writer.write(target)

            if not output_file.exists() or not output_file.is_file():
                return FileOperationResult(
                    action="combine_files",
                    status="FAILED",
                    error="Verification failed: combined output file was not created",
                    verified=False,
                )

            return FileOperationResult(
                action="combine_files",
                status="COMPLETED",
                path=PathValidator.normalize_path(output_file),
                message=f"Combined {len(resolved_files)} PDF files into {output_name}.",
                verified=True,
                details={
                    "files": [PathValidator.normalize_path(p) for p in resolved_files],
                    "output_name": output_name,
                    "count": len(resolved_files),
                },
            )

        except Exception as e:
            return FileOperationResult(
                action="combine_files",
                status="FAILED",
                error=str(e),
                details={"files": files, "destination_directory": destination_directory, "output_name": output_name},
            )

    @staticmethod
    def copy_item(source: str, destination: str) -> FileOperationResult:
        """Copy a file or folder with verification."""
        try:
            source_path = PathValidator.validate_read_path(source)
            dest_path = PathValidator.validate_write_path(destination)

            if not source_path.exists():
                return FileOperationResult(
                    action="copy_item",
                    status="FAILED",
                    error=f"Source not found: {source}",
                )

            # If destination is a directory, copy into it
            if dest_path.is_dir():
                final_dest = dest_path / source_path.name
            else:
                final_dest = dest_path

            # Check for conflicts
            if final_dest.exists():
                return FileOperationResult(
                    action="copy_item",
                    status="FAILED",
                    error=f"Destination already exists: {final_dest.name}",
                    details={"conflict": True},
                )

            # Ensure destination directory exists
            final_dest.parent.mkdir(parents=True, exist_ok=True)

            # Copy
            if source_path.is_file():
                shutil.copy2(str(source_path), str(final_dest))
            else:
                shutil.copytree(str(source_path), str(final_dest), dirs_exist_ok=False)

            # Verify
            if not final_dest.exists():
                return FileOperationResult(
                    action="copy_item",
                    status="FAILED",
                    error="Verification failed: destination does not exist",
                    verified=False,
                )

            return FileOperationResult(
                action="copy_item",
                status="COMPLETED",
                path=PathValidator.normalize_path(final_dest),
                message=f"Item copied to {PathValidator.get_relative_display_path(final_dest)}",
                verified=True,
                details={"source": PathValidator.normalize_path(source_path)},
            )

        except Exception as e:
            return FileOperationResult(
                action="copy_item",
                status="FAILED",
                error=str(e),
                details={"source": source, "destination": destination},
            )

    @staticmethod
    def delete_item(path: str) -> FileOperationResult:
        """Delete a file or folder with verification."""
        try:
            target_path = PathValidator.validate_write_path(path)

            if not target_path.exists():
                return FileOperationResult(
                    action="delete_item",
                    status="FAILED",
                    error=f"Item not found: {path}",
                )

            # Store path info before deletion for verification
            was_dir = target_path.is_dir()

            # Delete
            if was_dir:
                shutil.rmtree(str(target_path))
            else:
                target_path.unlink()

            # Verify deletion
            if target_path.exists():
                return FileOperationResult(
                    action="delete_item",
                    status="FAILED",
                    error="Verification failed: item still exists after deletion",
                    verified=False,
                )

            item_type = "folder" if was_dir else "file"
            return FileOperationResult(
                action="delete_item",
                status="COMPLETED",
                path=PathValidator.normalize_path(target_path),
                message=f"{item_type.capitalize()} deleted successfully.",
                verified=True,
                details={"type": item_type},
            )

        except Exception as e:
            return FileOperationResult(
                action="delete_item",
                status="FAILED",
                error=str(e),
                details={"path": path},
            )

    @staticmethod
    def list_directory(path: str) -> FileOperationResult:
        """List directory contents."""
        try:
            target_path = PathValidator.validate_read_path(path)

            if not target_path.exists():
                return FileOperationResult(
                    action="list_directory",
                    status="FAILED",
                    error=f"Directory not found: {path}",
                )

            if not target_path.is_dir():
                return FileOperationResult(
                    action="list_directory",
                    status="FAILED",
                    error=f"Not a directory: {path}",
                )

            items = []
            for item in sorted(target_path.iterdir()):
                items.append(
                    {
                        "name": item.name,
                        "path": PathValidator.normalize_path(item),
                        "type": "folder" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None,
                    }
                )

            return FileOperationResult(
                action="list_directory",
                status="COMPLETED",
                path=PathValidator.normalize_path(target_path),
                message=f"Found {len(items)} items.",
                verified=True,
                details={"items": items, "count": len(items)},
            )

        except Exception as e:
            return FileOperationResult(
                action="list_directory",
                status="FAILED",
                error=str(e),
                details={"path": path},
            )

    @staticmethod
    def find_files(path: str, pattern: Optional[str] = None) -> FileOperationResult:
        """Find files matching a pattern."""
        try:
            target_path = PathValidator.validate_read_path(path)

            if not target_path.exists():
                return FileOperationResult(
                    action="find_files",
                    status="FAILED",
                    error=f"Directory not found: {path}",
                )

            if not target_path.is_dir():
                return FileOperationResult(
                    action="find_files",
                    status="FAILED",
                    error=f"Not a directory: {path}",
                )

            # Find files
            files = []
            if pattern:
                # If pattern is an extension like "pdf" or ".pdf", search for *.pdf
                if not pattern.startswith("*."):
                    if pattern.startswith("."):
                        pattern = f"*{pattern}"  # ".pdf" -> "*.pdf"
                    elif not pattern.startswith("*"):
                        pattern = f"*.{pattern}"  # "pdf" -> "*.pdf"

                files = list(target_path.rglob(pattern))
            else:
                files = [p for p in target_path.rglob("*") if p.is_file()]

            file_info = []
            for f in sorted(files):
                file_info.append(
                    {
                        "name": f.name,
                        "path": PathValidator.normalize_path(f),
                        "size": f.stat().st_size,
                    }
                )

            return FileOperationResult(
                action="find_files",
                status="COMPLETED",
                path=PathValidator.normalize_path(target_path),
                message=f"Found {len(file_info)} files.",
                verified=True,
                details={"files": file_info, "count": len(file_info)},
            )

        except Exception as e:
            return FileOperationResult(
                action="find_files",
                status="FAILED",
                error=str(e),
                details={"path": path, "pattern": pattern},
            )

    @staticmethod
    def open_in_explorer(path: str) -> FileOperationResult:
        """Open path in Windows File Explorer."""
        try:
            target_path = PathValidator.validate_read_path(path)

            if not target_path.exists():
                return FileOperationResult(
                    action="open_in_explorer",
                    status="FAILED",
                    error=f"Path not found: {path}",
                )

            # Use explorer.exe with safe subprocess call
            if target_path.is_dir():
                subprocess.Popen(["explorer.exe", str(target_path)])
            else:
                # If file, open the containing folder and select the file
                subprocess.Popen(f'explorer.exe /select,"{target_path}"')

            return FileOperationResult(
                action="open_in_explorer",
                status="COMPLETED",
                path=PathValidator.normalize_path(target_path),
                message=f"Opened in File Explorer.",
                verified=True,
            )

        except Exception as e:
            return FileOperationResult(
                action="open_in_explorer",
                status="FAILED",
                error=str(e),
                details={"path": path},
            )

    @staticmethod
    def exists(path: str) -> FileOperationResult:
        """Check if path exists."""
        try:
            target_path = PathValidator.validate_read_path(path)
            exists = target_path.exists()

            if not exists:
                return FileOperationResult(
                    action="exists",
                    status="COMPLETED",
                    path=PathValidator.normalize_path(target_path),
                    message="Path does not exist.",
                    verified=True,
                    details={"exists": False},
                )

            return FileOperationResult(
                action="exists",
                status="COMPLETED",
                path=PathValidator.normalize_path(target_path),
                message="Path exists.",
                verified=True,
                details={
                    "exists": True,
                    "type": "folder" if target_path.is_dir() else "file",
                },
            )

        except Exception as e:
            return FileOperationResult(
                action="exists",
                status="FAILED",
                error=str(e),
                details={"path": path},
            )
