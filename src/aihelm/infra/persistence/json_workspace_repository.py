from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aihelm.domain.models.workspace import Workspace
from aihelm.domain.ports.workspace_repository import WorkspaceRepository


def _workspace_to_dict(workspace: Workspace) -> dict[str, Any]:
    return {
        "id": workspace.id,
        "path": str(workspace.path),
        "name": workspace.name,
        "selected_at": workspace.selected_at.isoformat(),
        "is_active": workspace.is_active,
    }


def _dict_to_workspace(data: dict[str, Any]) -> Workspace:
    return Workspace(
        id=data["id"],
        path=Path(data["path"]),
        name=data["name"],
        selected_at=datetime.fromisoformat(data["selected_at"]).replace(tzinfo=UTC),
        is_active=bool(data["is_active"]),
    )


class JsonWorkspaceRepository(WorkspaceRepository):
    """WorkspaceRepository backed by a JSON file with atomic writes."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.Lock()

    def _read_all(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        raw = self._path.read_text(encoding="utf-8")
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            msg = "Workspace file must contain a JSON list"
            raise ValueError(msg)
        if not all(isinstance(item, dict) for item in parsed):
            msg = "Workspace file list items must be JSON objects"
            raise ValueError(msg)
        return parsed

    def _write_all(self, workspaces: list[dict[str, Any]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(workspaces, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        tmp.replace(self._path)

    def list_all(self) -> list[Workspace]:
        with self._lock:
            items = self._read_all()
        return sorted(
            (_dict_to_workspace(item) for item in items),
            key=lambda workspace: workspace.selected_at,
            reverse=True,
        )

    def get_active(self) -> Workspace | None:
        with self._lock:
            items = self._read_all()
        for item in items:
            if bool(item["is_active"]):
                return _dict_to_workspace(item)
        return None

    def upsert(self, workspace: Workspace) -> Workspace:
        normalized_path = str(workspace.path.resolve())
        with self._lock:
            items = self._read_all()
            for idx, item in enumerate(items):
                if str(Path(item["path"]).resolve()) == normalized_path:
                    persisted = Workspace(
                        id=item["id"],
                        path=workspace.path,
                        name=workspace.name,
                        selected_at=workspace.selected_at,
                        is_active=workspace.is_active,
                    )
                    items[idx] = _workspace_to_dict(persisted)
                    self._write_all(items)
                    return persisted

            items.append(_workspace_to_dict(workspace))
            self._write_all(items)
        return workspace

    def set_active(self, workspace_id: str) -> Workspace:
        with self._lock:
            items = self._read_all()
            active_idx = -1
            for idx, item in enumerate(items):
                item["is_active"] = item["id"] == workspace_id
                if item["is_active"]:
                    active_idx = idx

            if active_idx == -1:
                msg = f"Workspace not found: {workspace_id}"
                raise ValueError(msg)

            self._write_all(items)
            return _dict_to_workspace(items[active_idx])

    def remove(self, workspace_id: str) -> None:
        with self._lock:
            items = [item for item in self._read_all() if item["id"] != workspace_id]
            self._write_all(items)
