"""Tests for envault.access module."""
import pytest
from pathlib import Path
from envault.access import (
    add_rule, remove_rule, load_rules, check_access, save_rules, AccessRule
)


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "vault.db")


def test_load_rules_no_file_returns_empty(vault_path):
    assert load_rules(vault_path) == []


def test_add_rule_and_load(vault_path):
    add_rule(vault_path, "API_KEY", "read")
    rules = load_rules(vault_path)
    assert len(rules) == 1
    assert rules[0].key == "API_KEY"
    assert rules[0].permission == "read"
    assert rules[0].identity == "default"


def test_add_rule_overwrites_existing(vault_path):
    add_rule(vault_path, "API_KEY", "read")
    add_rule(vault_path, "API_KEY", "deny")
    rules = load_rules(vault_path)
    assert len(rules) == 1
    assert rules[0].permission == "deny"


def test_add_rule_invalid_permission_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid permission"):
        add_rule(vault_path, "API_KEY", "execute")


def test_remove_rule(vault_path):
    add_rule(vault_path, "API_KEY", "read")
    remove_rule(vault_path, "API_KEY")
    assert load_rules(vault_path) == []


def test_remove_nonexistent_rule_is_noop(vault_path):
    remove_rule(vault_path, "MISSING")  # should not raise


def test_check_access_default_allow(vault_path):
    assert check_access(vault_path, "API_KEY", "read") is True
    assert check_access(vault_path, "API_KEY", "write") is True


def test_check_access_deny_rule(vault_path):
    add_rule(vault_path, "SECRET", "deny")
    assert check_access(vault_path, "SECRET", "read") is False
    assert check_access(vault_path, "SECRET", "write") is False


def test_check_access_read_only(vault_path):
    add_rule(vault_path, "TOKEN", "read")
    assert check_access(vault_path, "TOKEN", "read") is True
    assert check_access(vault_path, "TOKEN", "write") is False


def test_check_access_write_implies_read(vault_path):
    add_rule(vault_path, "TOKEN", "write")
    assert check_access(vault_path, "TOKEN", "read") is True
    assert check_access(vault_path, "TOKEN", "write") is True


def test_multiple_identities(vault_path):
    add_rule(vault_path, "DB_PASS", "read", identity="alice")
    add_rule(vault_path, "DB_PASS", "deny", identity="bob")
    assert check_access(vault_path, "DB_PASS", "read", identity="alice") is True
    assert check_access(vault_path, "DB_PASS", "read", identity="bob") is False
    assert check_access(vault_path, "DB_PASS", "read", identity="charlie") is True
