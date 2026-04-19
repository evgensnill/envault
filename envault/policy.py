"""Policy enforcement for vault keys (required keys, value constraints)."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

POLICY_FILENAME = ".envault-policy.json"


@dataclass
class PolicyRule:
    key: str
    required: bool = False
    min_length: int = 0
    pattern: str | None = None  # regex
    allowed_values: list[str] = field(default_factory=list)


@dataclass
class PolicyViolation:
    key: str
    rule: str
    message: str


def load_policy(vault_path: Path) -> list[PolicyRule]:
    policy_file = vault_path.parent / POLICY_FILENAME
    if not policy_file.exists():
        return []
    data = json.loads(policy_file.read_text())
    rules = []
    for entry in data.get("rules", []):
        rules.append(PolicyRule(
            key=entry["key"],
            required=entry.get("required", False),
            min_length=entry.get("min_length", 0),
            pattern=entry.get("pattern"),
            allowed_values=entry.get("allowed_values", []),
        ))
    return rules


def save_policy(vault_path: Path, rules: list[PolicyRule]) -> None:
    policy_file = vault_path.parent / POLICY_FILENAME
    data = {"rules": [
        {k: v for k, v in {
            "key": r.key,
            "required": r.required,
            "min_length": r.min_length,
            "pattern": r.pattern,
            "allowed_values": r.allowed_values,
        }.items() if v not in (False, 0, None, [])}
        for r in rules
    ]}
    policy_file.write_text(json.dumps(data, indent=2))


def check_policy(vault: Any, rules: list[PolicyRule]) -> list[PolicyViolation]:
    import re
    violations: list[PolicyViolation] = []
    keys = vault.list_keys()
    for rule in rules:
        if rule.required and rule.key not in keys:
            violations.append(PolicyViolation(rule.key, "required", f"{rule.key!r} is required but missing"))
            continue
        if rule.key not in keys:
            continue
        value = vault.get(rule.key)
        if rule.min_length and len(value) < rule.min_length:
            violations.append(PolicyViolation(rule.key, "min_length", f"{rule.key!r} must be at least {rule.min_length} chars"))
        if rule.pattern and not re.fullmatch(rule.pattern, value):
            violations.append(PolicyViolation(rule.key, "pattern", f"{rule.key!r} does not match pattern {rule.pattern!r}"))
        if rule.allowed_values and value not in rule.allowed_values:
            violations.append(PolicyViolation(rule.key, "allowed_values", f"{rule.key!r} value not in allowed list"))
    return violations
