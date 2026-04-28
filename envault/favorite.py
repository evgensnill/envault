"""Favorite keys — mark vault keys as favorites for quick access."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


def _favorites_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".favorites.json")


def _load(vault_path: str) -> List[str]:
    p = _favorites_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save(vault_path: str, favorites: List[str]) -> None:
    _favorites_path(vault_path).write_text(json.dumps(favorites, indent=2))


def add_favorite(vault_path: str, key: str, vault) -> None:
    """Mark *key* as a favorite. Raises KeyError if key not in vault."""
    if key not in vault.list_keys():
        raise KeyError(f"Key '{key}' not found in vault.")
    favorites = _load(vault_path)
    if key not in favorites:
        favorites.append(key)
        _save(vault_path, favorites)


def remove_favorite(vault_path: str, key: str) -> bool:
    """Remove *key* from favorites. Returns True if it was present."""
    favorites = _load(vault_path)
    if key in favorites:
        favorites.remove(key)
        _save(vault_path, favorites)
        return True
    return False


def is_favorite(vault_path: str, key: str) -> bool:
    return key in _load(vault_path)


def list_favorites(vault_path: str) -> List[str]:
    return list(_load(vault_path))


def clear_favorites(vault_path: str) -> int:
    """Remove all favorites. Returns count of cleared entries."""
    favorites = _load(vault_path)
    count = len(favorites)
    _save(vault_path, [])
    return count
