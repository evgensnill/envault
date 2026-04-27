"""Key priority management for envault.

Allows assigning priority levels to vault keys (low, normal, high, critical)
so operators can triage which secrets need attention first.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_PRIORITIES = ("low", "normal", "high", "critical")


def _priority_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".priorities.json")


def _load(vault_path: str) -> Dict[str, str]:
    p = _priority_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: Dict[str, str]) -> None:
    _priority_path(vault_path).write_text(json.dumps(data, indent=2))


def set_priority(vault_path: str, key: str, priority: str, vault_keys: List[str]) -> None:
    """Assign a priority level to *key*.

    Raises ValueError if the key does not exist in the vault or the
    priority level is not one of VALID_PRIORITIES.
    """
    if key not in vault_keys:
        raise KeyError(f"Key '{key}' not found in vault.")
    if priority not in VALID_PRIORITIES:
        raise ValueError(
            f"Invalid priority '{priority}'. Choose from: {', '.join(VALID_PRIORITIES)}"
        )
    data = _load(vault_path)
    data[key] = priority
    _save(vault_path, data)


def get_priority(vault_path: str, key: str) -> Optional[str]:
    """Return the priority for *key*, or None if not set."""
    return _load(vault_path).get(key)


def remove_priority(vault_path: str, key: str) -> bool:
    """Remove the priority entry for *key*. Returns True if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_by_priority(vault_path: str) -> Dict[str, List[str]]:
    """Return a mapping of priority level -> list of keys, sorted by level."""
    data = _load(vault_path)
    result: Dict[str, List[str]] = {level: [] for level in VALID_PRIORITIES}
    for key, level in data.items():
        result.setdefault(level, []).append(key)
    return result
