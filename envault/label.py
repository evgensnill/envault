"""Human-readable labels for vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


def _label_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".labels.json")


def _load(vault_path: str) -> Dict[str, str]:
    p = _label_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: Dict[str, str]) -> None:
    _label_path(vault_path).write_text(json.dumps(data, indent=2))


def set_label(vault_path: str, key: str, label: str, vault_keys: list[str]) -> None:
    """Assign a human-readable label to *key*.

    Raises KeyError if *key* does not exist in the vault.
    Raises ValueError if *label* is empty or blank.
    """
    if key not in vault_keys:
        raise KeyError(f"Key '{key}' not found in vault.")
    label = label.strip()
    if not label:
        raise ValueError("Label must not be empty.")
    data = _load(vault_path)
    data[key] = label
    _save(vault_path, data)


def remove_label(vault_path: str, key: str) -> bool:
    """Remove the label for *key*. Returns True if a label existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def get_label(vault_path: str, key: str) -> Optional[str]:
    """Return the label for *key*, or None if not set."""
    return _load(vault_path).get(key)


def list_labels(vault_path: str) -> Dict[str, str]:
    """Return all key→label mappings."""
    return dict(_load(vault_path))


def keys_with_label(vault_path: str, label: str) -> list[str]:
    """Return all keys whose label equals *label* (case-insensitive)."""
    label_lower = label.strip().lower()
    return [
        k for k, v in _load(vault_path).items()
        if v.strip().lower() == label_lower
    ]
