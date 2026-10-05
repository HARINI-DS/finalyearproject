from backend.memory.database import init_db
from backend.security.permission_manager import PermissionManager


def test_permission_grant_and_revoke():
    init_db()
    manager = PermissionManager()
    manager.grant("file_access", ["C:\\tmp"])
    assert manager.has_permission("file_access", "C:\\tmp")

    manager.revoke("file_access", ["C:\\tmp"])
    assert not manager.has_permission("file_access", "C:\\tmp")
