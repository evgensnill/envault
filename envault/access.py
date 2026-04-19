"""Access control: define and enforce key-level read/write permissions."""
from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal

Permission = Literal["read", "write", "deny"]


@dataclass
class AccessRule:
    key: str
    permission: Permission
    identity: str = "default"


def _access_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ".envault_access.json"


def load_rules(vault_path: str) -> list[AccessRule]:
    p = _access_path(vault_path)
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    return [AccessRule(**r) for r in data]


def save_rules(vault_path: str, rules: list[AccessRule]) -> None:
    p = _access_path(vault_path)
    p.write_text(json.dumps([r.__dict__ for r in rules], indent=2))


def add_rule(vault_path: str, key: str, permission: Permission, identity: str = "default") -> None:
    if permission not in ("read", "write", "deny"):
        raise ValueError(f"Invalid permission: {permission}")
    rules = load_rules(vault_path)
    rules = [r for r in rules if not (r.key == key and r.identity == identity)]
    rules.append(AccessRule(key=key, permission=permission, identity=identity))
    save_rules(vault_path, rules)


def remove_rule(vault_path: str, key: str, identity: str = "default") -> None:
    rules = load_rules(vault_path)
    rules = [r for r in rules if not (r.key == key and r.identity == identity)]
    save_rules(vault_path, rules)


def check_access(vault_path: str, key: str, action: Literal["read", "write"], identity: str = "default") -> bool:
    """Return True if identity is allowed to perform action on key."""
    rules = load_rules(vault_path)
    for r in rules:
        if r.key == key and r.identity == identity:
            if r.permission == "deny":
                return False
            if r.permission == action or r.permission == "write":  # write implies read
                return True
    # default allow if no rule
    return True
