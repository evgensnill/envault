"""Workspace management: group multiple vault paths under named workspaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_WORKSPACES_FILE = Path.home() / ".envault" / "workspaces.json"


def _load_workspaces() -> Dict[str, dict]:
    if not _WORKSPACES_FILE.exists():
        return {}
    with _WORKSPACES_FILE.open() as f:
        return json.load(f)


def _save_workspaces(data: Dict[str, dict]) -> None:
    _WORKSPACES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _WORKSPACES_FILE.open("w") as f:
        json.dump(data, f, indent=2)


def add_workspace(name: str, vault_path: str, description: str = "") -> None:
    """Register a named workspace pointing to a vault file."""
    data = _load_workspaces()
    data[name] = {"vault_path": vault_path, "description": description}
    _save_workspaces(data)


def remove_workspace(name: str) -> None:
    """Remove a workspace by name."""
    data = _load_workspaces()
    if name not in data:
        raise KeyError(f"Workspace '{name}' not found.")
    del data[name]
    _save_workspaces(data)


def get_workspace(name: str) -> dict:
    """Return workspace metadata dict with keys 'vault_path' and 'description'."""
    data = _load_workspaces()
    if name not in data:
        raise KeyError(f"Workspace '{name}' not found.")
    return data[name]


def list_workspaces() -> List[str]:
    """Return sorted list of workspace names."""
    return sorted(_load_workspaces().keys())


def set_active_workspace(name: str) -> None:
    """Mark a workspace as the active default."""
    data = _load_workspaces()
    if name not in data:
        raise KeyError(f"Workspace '{name}' not found.")
    for k in data:
        data[k]["active"] = k == name
    _save_workspaces(data)


def get_active_workspace() -> Optional[str]:
    """Return the name of the active workspace, or None."""
    data = _load_workspaces()
    for name, meta in data.items():
        if meta.get("active"):
            return name
    return None
