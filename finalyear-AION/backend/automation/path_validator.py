"""Path validation and normalization for safe filesystem operations."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


class PathValidator:
    """Validates and normalizes filesystem paths for security."""

    # System-critical directories to protect
    PROTECTED_DIRECTORIES = {
        "C:\\Windows",
        "C:\\System32",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\ProgramData",
    }

    # Allowed base directories for user file operations
    ALLOWED_USER_DIRECTORIES = {
        Path.home() / "Downloads",
        Path.home() / "Documents",
        Path.home() / "Desktop",
        Path.home(),
    }

    @staticmethod
    def resolve_user_path(path_str: str) -> Path:
        """
        Convert user-friendly path notation to absolute path.

        Examples:
            "Downloads" -> "C:\\Users\\User\\Downloads"
            "Downloads/AI2" -> "C:\\Users\\User\\Downloads\\AI2"
            "~/Documents" -> "C:\\Users\\User\\Documents"
        """
        if not path_str:
            raise ValueError("Path cannot be empty")

        # Handle common shortcuts
        path_str = path_str.replace("~", str(Path.home()))
        path_str = path_str.replace("./", str(Path.home()) + "/")

        # Handle friendly directory names
        friendly_dirs = {
            "downloads": Path.home() / "Downloads",
            "documents": Path.home() / "Documents",
            "desktop": Path.home() / "Desktop",
            "home": Path.home(),
        }

        parts = path_str.split("/")
        base = friendly_dirs.get(parts[0].lower())

        if base:
            # Reconstruct path using resolved base
            if len(parts) > 1:
                resolved = base / "/".join(parts[1:])
            else:
                resolved = base
        else:
            # Use path as-is if not a friendly name
            resolved = Path(path_str)

        # Convert to absolute path
        if not resolved.is_absolute():
            resolved = Path.cwd() / resolved

        # Normalize to handle .. and .
        try:
            resolved = resolved.resolve()
        except (OSError, RuntimeError):
            # If resolve fails (path doesn't exist), use expanduser
            resolved = resolved.expanduser()

        return resolved

    @staticmethod
    def is_path_traversal_attempt(path: Path) -> bool:
        """Detect path traversal attempts."""
        try:
            path.relative_to(path.resolve())
        except ValueError:
            return True
        return False

    @staticmethod
    def is_protected(path: Path) -> bool:
        """Check if path is in a protected system directory."""
        try:
            path_str = str(path).upper()
            for protected in PathValidator.PROTECTED_DIRECTORIES:
                if path_str.startswith(protected.upper()):
                    return True
        except Exception:
            pass
        return False

    @staticmethod
    def validate_write_path(path: str) -> Path:
        """
        Validate that a path is safe for write operations.

        Returns the resolved path.
        Raises ValueError if path is invalid or unsafe.
        """
        try:
            resolved = PathValidator.resolve_user_path(path)
        except Exception as e:
            raise ValueError(f"Invalid path: {e}")

        if PathValidator.is_protected(resolved):
            raise ValueError(f"Access denied: {resolved} is a protected system directory")

        if PathValidator.is_path_traversal_attempt(resolved):
            raise ValueError(f"Path traversal detected: {path}")

        return resolved

    @staticmethod
    def validate_read_path(path: str) -> Path:
        """
        Validate that a path is safe for read operations.

        Returns the resolved path.
        Raises ValueError if path is invalid or unsafe.
        """
        return PathValidator.validate_write_path(path)

    @staticmethod
    def normalize_path(path: Path) -> str:
        """Return normalized path string maintaining backslashes on Windows."""
        # On Windows, keep backslashes as stored in the database
        # On Unix, keep forward slashes
        return str(path)

    @staticmethod
    def get_relative_display_path(path: Path) -> str:
        """Get a user-friendly relative path for display."""
        try:
            # Try to make it relative to home
            return str(path.relative_to(Path.home())).replace("\\", "/")
        except ValueError:
            # If not under home, return normalized absolute path
            return PathValidator.normalize_path(path)
