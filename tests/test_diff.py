"""Tests for envault.diff."""
from __future__ import annotations

import pytest

from envault.diff import diff_vaults, diff_vault_vs_env
from envault.vault import Vault


def _make_vault(tmp_path, name: str, password: str, data: dict) -> Vault:
    path = str(tmp_path / name)
    v = Vault(path, password)
    for k, val in data.items():
        v.set(k, val)
    v.save()
    return v


def test_diff_vaults_added(tmp_path):
    a = _make_vault(tmp_path, "a.vault", "pw", {"FOO": "1"})
    b = _make_vault(tmp_path, "b.vault", "pw", {"FOO": "1", "BAR": "2"})
    entries = diff_vaults(a, b)
    assert len(entries) == 1
    assert entries[0].key == "BAR"
    assert entries[0].status == "added"
    assert entries[0].new_value == "2"


def test_diff_vaults_removed(tmp_path):
    a = _make_vault(tmp_path, "a.vault", "pw", {"FOO": "1", "BAR": "2"})
    b = _make_vault(tmp_path, "b.vault", "pw", {"FOO": "1"})
    entries = diff_vaults(a, b)
    assert len(entries) == 1
    assert entries[0].key == "BAR"
    assert entries[0].status == "removed"


def test_diff_vaults_changed(tmp_path):
    a = _make_vault(tmp_path, "a.vault", "pw", {"FOO": "old"})
    b = _make_vault(tmp_path, "b.vault", "pw", {"FOO": "new"})
    entries = diff_vaults(a, b)
    assert len(entries) == 1
    assert entries[0].status == "changed"
    assert entries[0].old_value == "old"
    assert entries[0].new_value == "new"


def test_diff_vaults_no_diff(tmp_path):
    a = _make_vault(tmp_path, "a.vault", "pw", {"FOO": "1"})
    b = _make_vault(tmp_path, "b.vault", "pw", {"FOO": "1"})
    entries = diff_vaults(a, b)
    assert entries == []


def test_diff_vaults_show_unchanged(tmp_path):
    a = _make_vault(tmp_path, "a.vault", "pw", {"FOO": "1"})
    b = _make_vault(tmp_path, "b.vault", "pw", {"FOO": "1"})
    entries = diff_vaults(a, b, show_unchanged=True)
    assert len(entries) == 1
    assert entries[0].status == "unchanged"


def test_diff_vault_vs_env_added(tmp_path):
    v = _make_vault(tmp_path, "v.vault", "pw", {"FOO": "1"})
    entries = diff_vault_vs_env(v, {"FOO": "1", "NEW": "x"})
    assert any(e.key == "NEW" and e.status == "added" for e in entries)


def test_diff_vault_vs_env_changed(tmp_path):
    v = _make_vault(tmp_path, "v.vault", "pw", {"FOO": "old"})
    entries = diff_vault_vs_env(v, {"FOO": "new"})
    assert entries[0].status == "changed"
    assert entries[0].old_value == "old"
    assert entries[0].new_value == "new"


def test_diff_vault_vs_env_removed(tmp_path):
    v = _make_vault(tmp_path, "v.vault", "pw", {"FOO": "1", "GONE": "bye"})
    entries = diff_vault_vs_env(v, {"FOO": "1"})
    assert any(e.key == "GONE" and e.status == "removed" for e in entries)
