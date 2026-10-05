from __future__ import annotations

from pathlib import Path


class ParameterValidator:
    @staticmethod
    def require_keys(parameters: dict, keys: list[str]) -> None:
        missing = [k for k in keys if k not in parameters]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    @staticmethod
    def safe_name(name: str) -> bool:
        return all(c.isalnum() or c in {"_", "-", " ", "."} for c in name)

    @staticmethod
    def normalize_path(path: str | Path) -> Path:
        p = Path(path).expanduser().resolve()
        return p

    @staticmethod
    def ensure_under_scope(target: Path, scope: Path) -> None:
        target_resolved = target.resolve()
        scope_resolved = scope.resolve()
        if scope_resolved not in [target_resolved, *target_resolved.parents]:
            raise PermissionError("Target path is outside the approved scope")
