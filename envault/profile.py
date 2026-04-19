"""Profile management: named sets of vault configuration (path, env, etc.)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

_PROFILES_FILE = Path.home() / ".envault" / "profiles.json"


def _load_profiles() -> dict[str, Any]:
    if not _PROFILES_FILE.exists():
        return {}
    return json.loads(_PROFILES_FILE.read_text())


def _save_profiles(profiles: dict[str, Any]) -> None:
    _PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PROFILES_FILE.write_text(json.dumps(profiles, indent=2))


def add_profile(name: str, vault_path: str, description: str = "") -> None:
    profiles = _load_profiles()
    profiles[name] = {"vault_path": vault_path, "description": description}
    _save_profiles(profiles)


def remove_profile(name: str) -> None:
    profiles = _load_profiles()
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")
    del profiles[name]
    _save_profiles(profiles)


def get_profile(name: str) -> dict[str, Any]:
    profiles = _load_profiles()
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")
    return profiles[name]


def list_profiles() -> list[dict[str, Any]]:
    profiles = _load_profiles()
    return [{"name": k, **v} for k, v in profiles.items()]


def set_default_profile(name: str) -> None:
    profiles = _load_profiles()
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")
    profiles["__default__"] = name
    _save_profiles(profiles)


def get_default_profile() -> str | None:
    profiles = _load_profiles()
    return profiles.get("__default__")
