"""Tests for envault.inherit — vault inheritance."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.inherit import (
    clear_parent,
    effective_keys,
    get_parent,
    resolve_key,
    set_parent,
)


def _make_vault(tmp_path: Path, name: str, password: str, secrets: dict):
    """Create a minimal vault file and return its path + a Vault instance."""
    from envault.vault import Vault

    vault_file = tmp_path / name
    v = Vault(str(vault_file), password)
    v.load()  # initialises empty store
    for k, val in secrets.items():
        v.set(k, val)
    v.save()
    return vault_file, v


def test_set_parent_stores_path(tmp_path):
    child_file, _ = _make_vault(tmp_path, "child.vault", "pw", {})
    parent_file, _ = _make_vault(tmp_path, "parent.vault", "pw", {})

    set_parent(child_file, str(parent_file))
    assert get_parent(child_file) == str(parent_file.resolve())


def test_set_parent_missing_file_raises(tmp_path):
    child_file, _ = _make_vault(tmp_path, "child.vault", "pw", {})
    with pytest.raises(FileNotFoundError):
        set_parent(child_file, str(tmp_path / "nonexistent.vault"))


def test_get_parent_no_config_returns_none(tmp_path):
    child_file, _ = _make_vault(tmp_path, "child.vault", "pw", {})
    assert get_parent(child_file) is None


def test_clear_parent_removes_config(tmp_path):
    child_file, _ = _make_vault(tmp_path, "child.vault", "pw", {})
    parent_file, _ = _make_vault(tmp_path, "parent.vault", "pw", {})

    set_parent(child_file, str(parent_file))
    result = clear_parent(child_file)
    assert result is True
    assert get_parent(child_file) is None


def test_clear_parent_when_none_returns_false(tmp_path):
    child_file, _ = _make_vault(tmp_path, "child.vault", "pw", {})
    assert clear_parent(child_file) is False


def test_resolve_key_found_in_child(tmp_path):
    child_file, child = _make_vault(tmp_path, "child.vault", "pw", {"FOO": "bar"})
    parent_file, _ = _make_vault(tmp_path, "parent.vault", "pw", {"FOO": "parent_bar"})

    set_parent(child_file, str(parent_file))
    assert resolve_key(child, "FOO", "pw") == "bar"


def test_resolve_key_falls_back_to_parent(tmp_path):
    child_file, child = _make_vault(tmp_path, "child.vault", "pw", {})
    parent_file, _ = _make_vault(tmp_path, "parent.vault", "pw", {"PARENT_KEY": "secret"})

    set_parent(child_file, str(parent_file))
    assert resolve_key(child, "PARENT_KEY", "pw") == "secret"


def test_resolve_key_missing_everywhere_raises(tmp_path):
    child_file, child = _make_vault(tmp_path, "child.vault", "pw", {})
    parent_file, _ = _make_vault(tmp_path, "parent.vault", "pw", {})

    set_parent(child_file, str(parent_file))
    with pytest.raises(KeyError):
        resolve_key(child, "MISSING", "pw")


def test_effective_keys_merges_both_vaults(tmp_path):
    child_file, child = _make_vault(tmp_path, "child.vault", "pw", {"CHILD_KEY": "c"})
    parent_file, _ = _make_vault(tmp_path, "parent.vault", "pw", {"PARENT_KEY": "p"})

    set_parent(child_file, str(parent_file))
    keys = effective_keys(child, "pw")
    assert "CHILD_KEY" in keys
    assert "PARENT_KEY" in keys


def test_effective_keys_no_parent_returns_child_only(tmp_path):
    _, child = _make_vault(tmp_path, "child.vault", "pw", {"ONLY": "v"})
    keys = effective_keys(child, "pw")
    assert keys == ["ONLY"]
