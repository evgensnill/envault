"""Tests for envault.group."""
from __future__ import annotations

import pytest

from envault.group import (
    add_to_group,
    delete_group,
    get_group,
    list_groups,
    remove_from_group,
)


def _make_vault(tmp_path):
    """Return a (vault_path_str, vault_keys) pair with a simple file."""
    p = tmp_path / "vault.db"
    p.write_bytes(b"")
    return str(p), ["DB_HOST", "DB_PASS", "API_KEY", "SECRET"]


def test_add_and_get_group(tmp_path):
    vp, keys = _make_vault(tmp_path)
    add_to_group(vp, "database", "DB_HOST", keys)
    add_to_group(vp, "database", "DB_PASS", keys)
    assert get_group(vp, "database") == ["DB_HOST", "DB_PASS"]


def test_add_duplicate_is_idempotent(tmp_path):
    vp, keys = _make_vault(tmp_path)
    add_to_group(vp, "database", "DB_HOST", keys)
    add_to_group(vp, "database", "DB_HOST", keys)
    assert get_group(vp, "database").count("DB_HOST") == 1


def test_add_missing_key_raises(tmp_path):
    vp, keys = _make_vault(tmp_path)
    with pytest.raises(KeyError, match="MISSING"):
        add_to_group(vp, "database", "MISSING", keys)


def test_add_invalid_group_name_raises(tmp_path):
    vp, keys = _make_vault(tmp_path)
    with pytest.raises(ValueError, match="Invalid group name"):
        add_to_group(vp, "bad-name!", "DB_HOST", keys)


def test_remove_from_group(tmp_path):
    vp, keys = _make_vault(tmp_path)
    add_to_group(vp, "database", "DB_HOST", keys)
    add_to_group(vp, "database", "DB_PASS", keys)
    removed = remove_from_group(vp, "database", "DB_HOST")
    assert removed is True
    assert get_group(vp, "database") == ["DB_PASS"]


def test_remove_last_key_deletes_group(tmp_path):
    vp, keys = _make_vault(tmp_path)
    add_to_group(vp, "solo", "API_KEY", keys)
    remove_from_group(vp, "solo", "API_KEY")
    assert "solo" not in list_groups(vp)


def test_remove_nonexistent_key_returns_false(tmp_path):
    vp, keys = _make_vault(tmp_path)
    assert remove_from_group(vp, "database", "DB_HOST") is False


def test_list_groups_empty(tmp_path):
    vp, _ = _make_vault(tmp_path)
    assert list_groups(vp) == {}


def test_list_groups_multiple(tmp_path):
    vp, keys = _make_vault(tmp_path)
    add_to_group(vp, "database", "DB_HOST", keys)
    add_to_group(vp, "auth", "API_KEY", keys)
    add_to_group(vp, "auth", "SECRET", keys)
    data = list_groups(vp)
    assert set(data.keys()) == {"database", "auth"}
    assert data["auth"] == ["API_KEY", "SECRET"]


def test_delete_group(tmp_path):
    vp, keys = _make_vault(tmp_path)
    add_to_group(vp, "database", "DB_HOST", keys)
    assert delete_group(vp, "database") is True
    assert get_group(vp, "database") == []


def test_delete_nonexistent_group_returns_false(tmp_path):
    vp, _ = _make_vault(tmp_path)
    assert delete_group(vp, "nonexistent") is False


def test_get_group_missing_returns_empty(tmp_path):
    vp, _ = _make_vault(tmp_path)
    assert get_group(vp, "ghost") == []
