from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from backend.automation.path_validator import PathValidator
from backend.memory.database import SessionLocal
from backend.models.database_models import PermissionRecord


class PermissionManager:
    """Manages filesystem permissions with granular control."""

    # Map actions to required capabilities
    ACTION_CAPABILITY_MAP = {
        "create_folder": "WRITE",
        "create_file": "WRITE",
        "rename_item": "WRITE",
        "move_item": "WRITE",
        "move_file": "WRITE",
        "move_files": "WRITE",
        "copy_item": "WRITE",
        "delete_item": "DELETE",
        "list_directory": "READ",
        "find_files": "READ",
        "combine_files": "WRITE",
        "open_in_explorer": "READ",
        "exists": "READ",
    }

    def get_permissions(self) -> list[dict]:
        """Get all permissions."""
        with SessionLocal() as db:
            rows = db.execute(select(PermissionRecord)).scalars().all()
            return [
                {
                    "id": r.id,
                    "resource_path": r.scope,
                    "capability": r.capability,
                    "granted": r.granted,
                    "updated_at": r.updated_at.isoformat(),
                }
                for r in rows
            ]

    def grant(self, capability: str, scopes: list[str]) -> list[dict]:
        """Grant permissions for given scopes."""
        with SessionLocal() as db:
            for scope in scopes:
                row = db.execute(
                    select(PermissionRecord).where(
                        PermissionRecord.capability == capability,
                        PermissionRecord.scope == scope,
                    )
                ).scalar_one_or_none()
                if row:
                    row.granted = True
                    row.updated_at = datetime.utcnow()
                else:
                    db.add(
                        PermissionRecord(
                            capability=capability,
                            scope=scope,
                            granted=True,
                            updated_at=datetime.utcnow(),
                        )
                    )
            db.commit()
        return self.get_permissions()

    def revoke(self, capability: str, scopes: list[str]) -> list[dict]:
        """Revoke permissions for given scopes."""
        with SessionLocal() as db:
            for scope in scopes:
                row = db.execute(
                    select(PermissionRecord).where(
                        PermissionRecord.capability == capability,
                        PermissionRecord.scope == scope,
                    )
                ).scalar_one_or_none()
                if row:
                    row.granted = False
                    row.updated_at = datetime.utcnow()
            db.commit()
        return self.get_permissions()

    def has_permission(self, capability: str, scope: str) -> bool:
        """Check if a permission is granted."""
        with SessionLocal() as db:
            # Normalize scope
            try:
                scope_path = PathValidator.resolve_user_path(scope)
                scope_normalized = PathValidator.normalize_path(scope_path)
            except Exception:
                scope_normalized = scope

            # Check exact match and parent directory permissions
            row = db.execute(
                select(PermissionRecord).where(
                    PermissionRecord.capability == capability,
                    PermissionRecord.scope == scope_normalized,
                    PermissionRecord.granted.is_(True),
                )
            ).scalar_one_or_none()

            if row:
                return True

            # Check parent directories
            try:
                scope_path = PathValidator.resolve_user_path(scope)
                parent = scope_path.parent
                while parent != parent.parent:  # Until root
                    parent_normalized = PathValidator.normalize_path(parent)
                    row = db.execute(
                        select(PermissionRecord).where(
                            PermissionRecord.capability == capability,
                            PermissionRecord.scope == parent_normalized,
                            PermissionRecord.granted.is_(True),
                        )
                    ).scalar_one_or_none()
                    if row:
                        return True
                    parent = parent.parent
            except Exception:
                pass

            return False

    def check_action_permission(self, action: str, path: str) -> bool:
        """Check if an action is permitted on a path."""
        capability = self.ACTION_CAPABILITY_MAP.get(action)
        if not capability:
            # Unknown action - deny by default
            return False

        # Special handling for destructive operations
        if action == "delete_item":
            # Deletion always requires explicit permission
            return self.has_permission(capability, path)

        return self.has_permission(capability, path)

    def get_required_permission(self, action: str, path: str) -> Optional[dict]:
        """Get the required permission for an action if not already granted."""
        capability = self.ACTION_CAPABILITY_MAP.get(action)
        if not capability:
            return None

        if self.has_permission(capability, path):
            return None

        # Return the required permission
        try:
            resolved_path = PathValidator.resolve_user_path(path)
            normalized_path = PathValidator.normalize_path(resolved_path)
        except Exception:
            normalized_path = path

        return {
            "action": action,
            "path": normalized_path,
            "capability": capability,
            "message": f"{action} requires {capability} permission on {PathValidator.get_relative_display_path(Path(normalized_path))}",
        }
