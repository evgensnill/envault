"""Tests for envault.policy."""
import json
import pytest
from pathlib import Path
from envault.policy import (
    PolicyRule, PolicyViolation,
    load_policy, save_policy, check_policy, POLICY_FILENAME,
)


class _FakeVault:
    def __init__(self, data: dict):
        self._data = data

    def list_keys(self):
        return list(self._data.keys())

    def get(self, key):
        return self._data[key]


def _policy_path(tmp_path):
    fake_vault = tmp_path / "vault" / ".envault"
    fake_vault.parent.mkdir(parents=True, exist_ok=True)
    fake_vault.touch()
    return fake_vault


def test_load_policy_missing_file(tmp_path):
    vault_path = tmp_path / ".envault"
    assert load_policy(vault_path) == []


def test_save_and_load_roundtrip(tmp_path):
    vault_path = tmp_path / ".envault"
    rules = [
        PolicyRule(key="API_KEY", required=True, min_length=16),
        PolicyRule(key="ENV", allowed_values=["prod", "staging"]),
    ]
    save_policy(vault_path, rules)
    loaded = load_policy(vault_path)
    assert len(loaded) == 2
    assert loaded[0].key == "API_KEY"
    assert loaded[0].required is True
    assert loaded[0].min_length == 16
    assert loaded[1].allowed_values == ["prod", "staging"]


def test_check_policy_required_missing(tmp_path):
    vault = _FakeVault({})
    rules = [PolicyRule(key="SECRET", required=True)]
    violations = check_policy(vault, rules)
    assert len(violations) == 1
    assert violations[0].rule == "required"


def test_check_policy_min_length(tmp_path):
    vault = _FakeVault({"TOKEN": "short"})
    rules = [PolicyRule(key="TOKEN", min_length=10)]
    violations = check_policy(vault, rules)
    assert len(violations) == 1
    assert violations[0].rule == "min_length"


def test_check_policy_pattern(tmp_path):
    vault = _FakeVault({"PORT": "abc"})
    rules = [PolicyRule(key="PORT", pattern=r"\d+")]
    violations = check_policy(vault, rules)
    assert violations[0].rule == "pattern"


def test_check_policy_allowed_values(tmp_path):
    vault = _FakeVault({"ENV": "dev"})
    rules = [PolicyRule(key="ENV", allowed_values=["prod", "staging"])]
    violations = check_policy(vault, rules)
    assert violations[0].rule == "allowed_values"


def test_check_policy_no_violations(tmp_path):
    vault = _FakeVault({"API_KEY": "supersecretvalue", "ENV": "prod"})
    rules = [
        PolicyRule(key="API_KEY", required=True, min_length=8),
        PolicyRule(key="ENV", allowed_values=["prod", "staging"]),
    ]
    violations = check_policy(vault, rules)
    assert violations == []


def test_optional_key_not_present_skips(tmp_path):
    vault = _FakeVault({})
    rules = [PolicyRule(key="OPTIONAL", min_length=5)]
    violations = check_policy(vault, rules)
    assert violations == []
