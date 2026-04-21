"""Tests for envault.schema module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.schema import (
    SchemaRule,
    SchemaViolation,
    add_rule,
    check_schema,
    load_schema,
    remove_rule,
    validate_value,
)


class _FakeVault:
    def __init__(self, store: dict[str, str]):
        self._store = store

    def list_keys(self):
        return list(self._store.keys())

    def get(self, key: str) -> str:
        return self._store[key]


def _vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "vault.env"
    p.touch()
    return p


def test_load_schema_no_file_returns_empty(tmp_path):
    vp = _vault_path(tmp_path)
    assert load_schema(vp) == []


def test_add_rule_and_load(tmp_path):
    vp = _vault_path(tmp_path)
    rule = SchemaRule(key="API_KEY", type="string", required=True)
    add_rule(vp, rule)
    rules = load_schema(vp)
    assert len(rules) == 1
    assert rules[0].key == "API_KEY"
    assert rules[0].required is True


def test_add_rule_replaces_existing(tmp_path):
    vp = _vault_path(tmp_path)
    add_rule(vp, SchemaRule(key="PORT", type="string"))
    add_rule(vp, SchemaRule(key="PORT", type="integer"))
    rules = load_schema(vp)
    assert len(rules) == 1
    assert rules[0].type == "integer"


def test_add_rule_invalid_type_raises(tmp_path):
    vp = _vault_path(tmp_path)
    with pytest.raises(ValueError, match="Invalid type"):
        add_rule(vp, SchemaRule(key="X", type="uuid"))


def test_remove_rule_returns_true(tmp_path):
    vp = _vault_path(tmp_path)
    add_rule(vp, SchemaRule(key="SECRET", type="string"))
    assert remove_rule(vp, "SECRET") is True
    assert load_schema(vp) == []


def test_remove_rule_missing_returns_false(tmp_path):
    vp = _vault_path(tmp_path)
    assert remove_rule(vp, "NONEXISTENT") is False


def test_validate_value_integer_valid():
    rule = SchemaRule(key="PORT", type="integer")
    assert validate_value(rule, "8080") is None


def test_validate_value_integer_invalid():
    rule = SchemaRule(key="PORT", type="integer")
    v = validate_value(rule, "not-a-number")
    assert isinstance(v, SchemaViolation)
    assert "integer" in v.message


def test_validate_value_email_valid():
    rule = SchemaRule(key="EMAIL", type="email")
    assert validate_value(rule, "user@example.com") is None


def test_validate_value_custom_pattern_violation():
    rule = SchemaRule(key="TOKEN", type="string", pattern=r"^tok_")
    v = validate_value(rule, "abc123")
    assert v is not None
    assert "pattern" in v.message


def test_check_schema_missing_required_key(tmp_path):
    vp = _vault_path(tmp_path)
    add_rule(vp, SchemaRule(key="DB_URL", type="url", required=True))
    vault = _FakeVault({})
    violations = check_schema(vp, vault)
    assert any(v.key == "DB_URL" and "missing" in v.message for v in violations)


def test_check_schema_valid_vault_no_violations(tmp_path):
    vp = _vault_path(tmp_path)
    add_rule(vp, SchemaRule(key="PORT", type="integer", required=True))
    vault = _FakeVault({"PORT": "5432"})
    assert check_schema(vp, vault) == []


def test_check_schema_type_violation(tmp_path):
    vp = _vault_path(tmp_path)
    add_rule(vp, SchemaRule(key="RETRIES", type="integer"))
    vault = _FakeVault({"RETRIES": "many"})
    violations = check_schema(vp, vault)
    assert any(v.key == "RETRIES" for v in violations)
