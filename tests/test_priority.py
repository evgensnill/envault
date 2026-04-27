"""Tests for envault.priority."""

from __future__ import annotations

import pytest

from envault.priority import (
    VALID_PRIORITIES,
    get_priority,
    list_by_priority,
    remove_priority,
    set_priority,
)


@pytest.fixture()
def vault_path(tmp_path):
    vp = tmp_path / "test.vault"
    vp.write_text("{}")  # minimal vault file presence
    return str(vp)


VAULT_KEYS = ["DB_PASSWORD", "API_KEY", "SECRET_TOKEN", "DEBUG"]


def test_set_and_get_priority(vault_path):
    set_priority(vault_path, "DB_PASSWORD", "critical", VAULT_KEYS)
    assert get_priority(vault_path, "DB_PASSWORD") == "critical"


def test_get_priority_missing_key_returns_none(vault_path):
    assert get_priority(vault_path, "DB_PASSWORD") is None


def test_set_priority_missing_vault_key_raises(vault_path):
    with pytest.raises(KeyError, match="NOT_EXIST"):
        set_priority(vault_path, "NOT_EXIST", "high", VAULT_KEYS)


def test_set_priority_invalid_level_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid priority"):
        set_priority(vault_path, "DB_PASSWORD", "urgent", VAULT_KEYS)


def test_remove_priority_returns_true(vault_path):
    set_priority(vault_path, "API_KEY", "high", VAULT_KEYS)
    assert remove_priority(vault_path, "API_KEY") is True
    assert get_priority(vault_path, "API_KEY") is None


def test_remove_priority_missing_returns_false(vault_path):
    assert remove_priority(vault_path, "API_KEY") is False


def test_list_by_priority_groups_correctly(vault_path):
    set_priority(vault_path, "DB_PASSWORD", "critical", VAULT_KEYS)
    set_priority(vault_path, "API_KEY", "high", VAULT_KEYS)
    set_priority(vault_path, "SECRET_TOKEN", "high", VAULT_KEYS)
    set_priority(vault_path, "DEBUG", "low", VAULT_KEYS)

    grouped = list_by_priority(vault_path)

    assert "DB_PASSWORD" in grouped["critical"]
    assert set(grouped["high"]) == {"API_KEY", "SECRET_TOKEN"}
    assert "DEBUG" in grouped["low"]
    assert grouped["normal"] == []


def test_list_by_priority_empty_vault(vault_path):
    grouped = list_by_priority(vault_path)
    assert all(v == [] for v in grouped.values())
    assert set(grouped.keys()) == set(VALID_PRIORITIES)


def test_overwrite_priority(vault_path):
    set_priority(vault_path, "DB_PASSWORD", "low", VAULT_KEYS)
    set_priority(vault_path, "DB_PASSWORD", "critical", VAULT_KEYS)
    assert get_priority(vault_path, "DB_PASSWORD") == "critical"
