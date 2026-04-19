"""Tag management for vault keys."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envault.vault import Vault

_TAGS_META_KEY = "__tags__"


def _get_tags_store(vault: "Vault") -> dict[str, list[str]]:
    """Return the tags metadata dict (key -> list of tags)."""
    raw = vault.store.get(_TAGS_META_KEY, {})
    if not isinstance(raw, dict):
        return {}
    return raw


def _save_tags_store(vault: "Vault", store: dict[str, list[str]]) -> None:
    vault.store[_TAGS_META_KEY] = store
    vault.save()


def add_tag(vault: "Vault", key: str, tag: str) -> None:
    """Add a tag to a key. Raises KeyError if key not in vault."""
    if key not in vault.store or key == _TAGS_META_KEY:
        raise KeyError(f"Key '{key}' not found in vault.")
    store = _get_tags_store(vault)
    tags = store.get(key, [])
    if tag not in tags:
        tags.append(tag)
    store[key] = tags
    _save_tags_store(vault, store)


def remove_tag(vault: "Vault", key: str, tag: str) -> None:
    """Remove a tag from a key."""
    store = _get_tags_store(vault)
    tags = store.get(key, [])
    if tag in tags:
        tags.remove(tag)
    store[key] = tags
    _save_tags_store(vault, store)


def get_tags(vault: "Vault", key: str) -> list[str]:
    """Return tags for a given key."""
    store = _get_tags_store(vault)
    return list(store.get(key, []))


def keys_by_tag(vault: "Vault", tag: str) -> list[str]:
    """Return all keys that have the given tag."""
    store = _get_tags_store(vault)
    return [k for k, tags in store.items() if tag in tags]


def all_tags(vault: "Vault") -> dict[str, list[str]]:
    """Return the full tag mapping (excluding internal keys)."""
    return {k: list(v) for k, v in _get_tags_store(vault).items()}
