"""Tests for envault.sync module."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from envault.sync import SyncResult, diff_with_env, pull_from_env, push_to_env
from envault.vault import Vault

PASSWORD = "test-password"


def _make_vault(tmp_path: Path, secrets: dict | None = None) -> Vault:
    vault_file = tmp_path / "vault.enc"
    vault = Vault(str(vault_file), PASSWORD)
    if secrets:
        for k, v in secrets.items():
            vault.set(k, v)
    vault.save()
    return vault


def test_push_to_env_sets_variables(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path, {"APP_KEY": "secret1", "DB_URL": "postgres://localhost"})
    monkeypatch.delenv("APP_KEY", raising=False)
    monkeypatch.delenv("DB_URL", raising=False)
    result = push_to_env(vault)
    assert "APP_KEY" in result.pushed
    assert "DB_URL" in result.pushed
    assert os.environ["APP_KEY"] == "secret1"
    assert os.environ["DB_URL"] == "postgres://localhost"


def test_push_to_env_no_overwrite_skips_existing(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path, {"APP_KEY": "new_value"})
    monkeypatch.setenv("APP_KEY", "old_value")
    result = push_to_env(vault, overwrite=False)
    assert "APP_KEY" in result.skipped
    assert os.environ["APP_KEY"] == "old_value"


def test_push_to_env_specific_keys(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path, {"KEY_A": "a", "KEY_B": "b"})
    monkeypatch.delenv("KEY_A", raising=False)
    monkeypatch.delenv("KEY_B", raising=False)
    result = push_to_env(vault, keys=["KEY_A"])
    assert "KEY_A" in result.pushed
    assert "KEY_B" not in result.pushed


def test_pull_from_env_adds_to_vault(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path)
    monkeypatch.setenv("PULLED_KEY", "pulled_value")
    result = pull_from_env(vault, keys=["PULLED_KEY"])
    assert "PULLED_KEY" in result.pulled
    assert vault.get("PULLED_KEY") == "pulled_value"


def test_pull_from_env_no_overwrite_records_conflict(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path, {"CONFLICT_KEY": "vault_value"})
    monkeypatch.setenv("CONFLICT_KEY", "env_value")
    result = pull_from_env(vault, keys=["CONFLICT_KEY"], overwrite=False)
    assert "CONFLICT_KEY" in result.conflicts
    assert vault.get("CONFLICT_KEY") == "vault_value"


def test_pull_from_env_skips_missing_env_key(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path)
    monkeypatch.delenv("NONEXISTENT_KEY", raising=False)
    result = pull_from_env(vault, keys=["NONEXISTENT_KEY"])
    assert "NONEXISTENT_KEY" in result.skipped


def test_diff_with_env_detects_missing(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path, {"MISSING_KEY": "value"})
    monkeypatch.delenv("MISSING_KEY", raising=False)
    diffs = diff_with_env(vault)
    assert "MISSING_KEY" in diffs
    assert diffs["MISSING_KEY"]["status"] == "missing_in_env"


def test_diff_with_env_detects_changed(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path, {"CHANGED_KEY": "vault_val"})
    monkeypatch.setenv("CHANGED_KEY", "env_val")
    diffs = diff_with_env(vault)
    assert "CHANGED_KEY" in diffs
    assert diffs["CHANGED_KEY"]["status"] == "changed"


def test_diff_with_env_no_diff_when_equal(tmp_path, monkeypatch):
    vault = _make_vault(tmp_path, {"SAME_KEY": "same_value"})
    monkeypatch.setenv("SAME_KEY", "same_value")
    diffs = diff_with_env(vault)
    assert "SAME_KEY" not in diffs
