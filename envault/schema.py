"""Schema validation for vault keys.

Allows defining expected types and patterns for keys so that
set/import operations can be validated against a schema.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


VALID_TYPES = {"string", "integer", "boolean", "url", "email"}

_TYPE_PATTERNS: dict[str, str] = {
    "integer": r"^-?\d+$",
    "boolean": r"^(true|false|1|0|yes|no)$",
    "url": r"^https?://.+",
    "email": r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
}


@dataclass
class SchemaRule:
    key: str
    type: str = "string"
    pattern: Optional[str] = None
    required: bool = False
    description: str = ""


@dataclass
class SchemaViolation:
    key: str
    message: str


def _schema_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".schema.json")


def load_schema(vault_path: Path) -> list[SchemaRule]:
    path = _schema_path(vault_path)
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return [SchemaRule(**entry) for entry in data]


def save_schema(vault_path: Path, rules: list[SchemaRule]) -> None:
    path = _schema_path(vault_path)
    path.write_text(
        json.dumps([r.__dict__ for r in rules], indent=2)
    )


def add_rule(vault_path: Path, rule: SchemaRule) -> None:
    if rule.type not in VALID_TYPES:
        raise ValueError(f"Invalid type '{rule.type}'. Must be one of {VALID_TYPES}.")
    rules = load_schema(vault_path)
    rules = [r for r in rules if r.key != rule.key]
    rules.append(rule)
    save_schema(vault_path, rules)


def remove_rule(vault_path: Path, key: str) -> bool:
    rules = load_schema(vault_path)
    new_rules = [r for r in rules if r.key != key]
    if len(new_rules) == len(rules):
        return False
    save_schema(vault_path, new_rules)
    return True


def validate_value(rule: SchemaRule, value: str) -> Optional[SchemaViolation]:
    """Validate a single value against its rule. Returns a violation or None."""
    if rule.type in _TYPE_PATTERNS:
        pat = _TYPE_PATTERNS[rule.type]
        if not re.match(pat, value, re.IGNORECASE):
            return SchemaViolation(rule.key, f"Value does not match type '{rule.type}'.")
    if rule.pattern and not re.search(rule.pattern, value):
        return SchemaViolation(rule.key, f"Value does not match pattern '{rule.pattern}'.")
    return None


def check_schema(vault_path: Path, vault) -> list[SchemaViolation]:
    """Check all schema rules against the current vault state."""
    rules = load_schema(vault_path)
    violations: list[SchemaViolation] = []
    existing_keys = set(vault.list_keys())
    for rule in rules:
        if rule.required and rule.key not in existing_keys:
            violations.append(SchemaViolation(rule.key, "Required key is missing."))
            continue
        if rule.key in existing_keys:
            value = vault.get(rule.key)
            v = validate_value(rule, value)
            if v:
                violations.append(v)
    return violations
