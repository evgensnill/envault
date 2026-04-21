"""Tests for envault.alias."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.alias import (
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    resolve_key,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    vp = tmp_path / "test.vault"
    vp.write_text("{}")  # minimal placeholder
    return vp


KEYS = ["DB_PASSWORD", "API_KEY", "SECRET_TOKEN"]


def test_add_alias_and_resolve(vault_path):
    add_alias(vault_path, "db_pass", "DB_PASSWORD", KEYS)
    assert resolve_alias(vault_path, "db_pass") == "DB_PASSWORD"


def test_add_alias_missing_key_raises(vault_path):
    with pytest.raises(KeyError, match="MISSING"):
        add_alias(vault_path, "gone", "MISSING", KEYS)


def test_add_alias_invalid_identifier_raises(vault_path):
    with pytest.raises(ValueError, match="not a valid identifier"):
        add_alias(vault_path, "my-alias", "DB_PASSWORD", KEYS)


def test_list_aliases_empty(vault_path):
    assert list_aliases(vault_path) == {}


def test_list_aliases_multiple(vault_path):
    add_alias(vault_path, "db_pass", "DB_PASSWORD", KEYS)
    add_alias(vault_path, "api", "API_KEY", KEYS)
    result = list_aliases(vault_path)
    assert result == {"db_pass": "DB_PASSWORD", "api": "API_KEY"}


def test_remove_alias_returns_true(vault_path):
    add_alias(vault_path, "db_pass", "DB_PASSWORD", KEYS)
    assert remove_alias(vault_path, "db_pass") is True
    assert resolve_alias(vault_path, "db_pass") is None


def test_remove_alias_missing_returns_false(vault_path):
    assert remove_alias(vault_path, "nonexistent") is False


def test_resolve_alias_no_file_returns_none(vault_path):
    assert resolve_alias(vault_path, "anything") is None


def test_resolve_key_direct(vault_path):
    assert resolve_key(vault_path, "DB_PASSWORD", KEYS) == "DB_PASSWORD"


def test_resolve_key_via_alias(vault_path):
    add_alias(vault_path, "db_pass", "DB_PASSWORD", KEYS)
    assert resolve_key(vault_path, "db_pass", KEYS) == "DB_PASSWORD"


def test_resolve_key_unknown_raises(vault_path):
    with pytest.raises(KeyError, match="neither a vault key nor a known alias"):
        resolve_key(vault_path, "ghost", KEYS)


def test_overwrite_alias(vault_path):
    add_alias(vault_path, "token", "API_KEY", KEYS)
    add_alias(vault_path, "token", "SECRET_TOKEN", KEYS)
    assert resolve_alias(vault_path, "token") == "SECRET_TOKEN"
