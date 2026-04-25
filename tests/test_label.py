"""Tests for envault.label."""
import pytest
from pathlib import Path
from envault.label import (
    set_label,
    remove_label,
    get_label,
    list_labels,
    keys_with_label,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> str:
    return str(tmp_path / "vault.env")


VAULT_KEYS = ["DB_HOST", "DB_PASS", "API_KEY"]


def test_set_and_get_label(vault_path):
    set_label(vault_path, "DB_HOST", "Database hostname", VAULT_KEYS)
    assert get_label(vault_path, "DB_HOST") == "Database hostname"


def test_get_label_missing_key_returns_none(vault_path):
    assert get_label(vault_path, "DB_HOST") is None


def test_set_label_missing_vault_key_raises(vault_path):
    with pytest.raises(KeyError, match="UNKNOWN"):
        set_label(vault_path, "UNKNOWN", "Some label", VAULT_KEYS)


def test_set_label_empty_label_raises(vault_path):
    with pytest.raises(ValueError, match="empty"):
        set_label(vault_path, "DB_HOST", "   ", VAULT_KEYS)


def test_set_label_strips_whitespace(vault_path):
    set_label(vault_path, "API_KEY", "  API token  ", VAULT_KEYS)
    assert get_label(vault_path, "API_KEY") == "API token"


def test_remove_label_returns_true(vault_path):
    set_label(vault_path, "DB_HOST", "Host", VAULT_KEYS)
    assert remove_label(vault_path, "DB_HOST") is True
    assert get_label(vault_path, "DB_HOST") is None


def test_remove_label_missing_returns_false(vault_path):
    assert remove_label(vault_path, "DB_HOST") is False


def test_list_labels_empty(vault_path):
    assert list_labels(vault_path) == {}


def test_list_labels_returns_all(vault_path):
    set_label(vault_path, "DB_HOST", "Host", VAULT_KEYS)
    set_label(vault_path, "API_KEY", "Token", VAULT_KEYS)
    result = list_labels(vault_path)
    assert result == {"DB_HOST": "Host", "API_KEY": "Token"}


def test_keys_with_label_case_insensitive(vault_path):
    set_label(vault_path, "DB_HOST", "Database", VAULT_KEYS)
    set_label(vault_path, "DB_PASS", "database", VAULT_KEYS)
    set_label(vault_path, "API_KEY", "Token", VAULT_KEYS)
    result = keys_with_label(vault_path, "DATABASE")
    assert set(result) == {"DB_HOST", "DB_PASS"}


def test_keys_with_label_no_match(vault_path):
    set_label(vault_path, "DB_HOST", "Host", VAULT_KEYS)
    assert keys_with_label(vault_path, "Nonexistent") == []


def test_overwrite_label(vault_path):
    set_label(vault_path, "DB_HOST", "Old label", VAULT_KEYS)
    set_label(vault_path, "DB_HOST", "New label", VAULT_KEYS)
    assert get_label(vault_path, "DB_HOST") == "New label"
    assert list(list_labels(vault_path).values()).count("Old label") == 0
