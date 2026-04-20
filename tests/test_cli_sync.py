"""Tests for envault.cli_sync CLI commands."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_sync import sync
from envault.vault import Vault

PASSWORD = "cli-sync-pass"


def _runner():
    return CliRunner(mix_stderr=False)


def _make_vault(tmp_path: Path, secrets: dict | None = None) -> str:
    vault_file = str(tmp_path / "vault.enc")
    vault = Vault(vault_file, PASSWORD)
    if secrets:
        for k, v in secrets.items():
            vault.set(k, v)
    vault.save()
    return vault_file


def test_diff_command_no_diff(tmp_path, monkeypatch):
    vault_path = _make_vault(tmp_path, {"MY_KEY": "myval"})
    monkeypatch.setenv("MY_KEY", "myval")
    result = _runner().invoke(sync, ["diff", vault_path, PASSWORD])
    assert result.exit_code == 0
    assert "in sync" in result.output


def test_diff_command_shows_changed(tmp_path, monkeypatch):
    vault_path = _make_vault(tmp_path, {"CHANGED": "vault_val"})
    monkeypatch.setenv("CHANGED", "env_val")
    result = _runner().invoke(sync, ["diff", vault_path, PASSWORD])
    assert result.exit_code == 0
    assert "CHANGED" in result.output
    assert "changed" in result.output


def test_diff_command_shows_missing(tmp_path, monkeypatch):
    vault_path = _make_vault(tmp_path, {"ABSENT": "some_val"})
    monkeypatch.delenv("ABSENT", raising=False)
    result = _runner().invoke(sync, ["diff", vault_path, PASSWORD])
    assert result.exit_code == 0
    assert "ABSENT" in result.output
    assert "missing_in_env" in result.output


def test_pull_command(tmp_path, monkeypatch):
    vault_path = _make_vault(tmp_path)
    monkeypatch.setenv("PULL_TEST", "pulled_value")
    result = _runner().invoke(sync, ["pull", vault_path, PASSWORD, "--key", "PULL_TEST"])
    assert result.exit_code == 0
    assert "1" in result.output


def test_pull_command_conflict_no_overwrite(tmp_path, monkeypatch):
    vault_path = _make_vault(tmp_path, {"EXIST_KEY": "original"})
    monkeypatch.setenv("EXIST_KEY", "from_env")
    result = _runner().invoke(
        sync, ["pull", vault_path, PASSWORD, "--key", "EXIST_KEY", "--no-overwrite"]
    )
    assert result.exit_code == 0
    assert "EXIST_KEY" in result.stderr
