"""Snapshot: save and restore point-in-time copies of a vault."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

from envault.vault import Vault


def _snapshot_dir(vault_path: Path) -> Path:
    d = vault_path.parent / ".snapshots"
    d.mkdir(exist_ok=True)
    return d


def save_snapshot(vault: Vault, label: Optional[str] = None) -> str:
    """Persist current vault secrets as a snapshot. Returns snapshot id."""
    ts = int(time.time())
    snap_id = f"{ts}" + (f"_{label}" if label else "")
    snap_dir = _snapshot_dir(Path(vault.path))
    snap_file = snap_dir / f"{snap_id}.json"

    data = {
        "snap_id": snap_id,
        "created_at": ts,
        "label": label,
        "secrets": {k: vault.get(k) for k in vault.list_keys()},
    }
    snap_file.write_text(json.dumps(data, indent=2))
    return snap_id


def list_snapshots(vault: Vault) -> List[dict]:
    """Return metadata for all snapshots, newest first."""
    snap_dir = _snapshot_dir(Path(vault.path))
    results = []
    for f in sorted(snap_dir.glob("*.json"), reverse=True):
        raw = json.loads(f.read_text())
        results.append({"snap_id": raw["snap_id"], "created_at": raw["created_at"], "label": raw.get("label")})
    return results


def restore_snapshot(vault: Vault, snap_id: str, overwrite: bool = True) -> List[str]:
    """Restore secrets from a snapshot into vault. Returns list of restored keys."""
    snap_dir = _snapshot_dir(Path(vault.path))
    snap_file = snap_dir / f"{snap_id}.json"
    if not snap_file.exists():
        raise FileNotFoundError(f"Snapshot '{snap_id}' not found.")

    data = json.loads(snap_file.read_text())
    restored = []
    for key, value in data["secrets"].items():
        if not overwrite and key in vault.list_keys():
            continue
        vault.set(key, value)
        restored.append(key)
    vault.save()
    return restored


def delete_snapshot(vault: Vault, snap_id: str) -> None:
    """Delete a snapshot by id."""
    snap_dir = _snapshot_dir(Path(vault.path))
    snap_file = snap_dir / f"{snap_id}.json"
    if not snap_file.exists():
        raise FileNotFoundError(f"Snapshot '{snap_id}' not found.")
    snap_file.unlink()
