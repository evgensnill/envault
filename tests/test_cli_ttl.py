"""CLI tests for the ttl command group."""
from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.cli_ttl import ttl
from envault import ttl as ttl_mod


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    p = tmp_path / "vault.db"
    p.write_text("{}")
    return str(p)


def _fake_vault(keys=None):
    v = MagicMock()
    v.list_keys.return_value = keys or ["API_KEY", "DB_PASS"]
    return v


def test_set_cmd(runner, vault_file):
    with patch("envault.cli_ttl._get_vault", return_value=_fake_vault()):
        result = runner.invoke(ttl, ["set", "API_KEY", "3600",
                                     "--vault", vault_file, "--password", "pw"])
    assert result.exit_code == 0
    assert "3600s" in result.output
    meta = ttl_mod.get_ttl(vault_file, "API_KEY")
    assert meta is not None


def test_set_cmd_unknown_key(runner, vault_file):
    with patch("envault.cli_ttl._get_vault", return_value=_fake_vault()):
        result = runner.invoke(ttl, ["set", "UNKNOWN", "60",
                                     "--vault", vault_file, "--password", "pw"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_get_cmd_no_ttl(runner, vault_file):
    result = runner.invoke(ttl, ["get", "API_KEY", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No TTL" in result.output


def test_get_cmd_with_ttl(runner, vault_file):
    ttl_mod.set_ttl(vault_file, "API_KEY", 3600)
    result = runner.invoke(ttl, ["get", "API_KEY", "--vault", vault_file])
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_remove_cmd(runner, vault_file):
    ttl_mod.set_ttl(vault_file, "DB_PASS", 60)
    result = runner.invoke(ttl, ["remove", "DB_PASS", "--vault", vault_file])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_cmd_empty(runner, vault_file):
    result = runner.invoke(ttl, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No TTLs" in result.output


def test_list_cmd_with_entries(runner, vault_file):
    ttl_mod.set_ttl(vault_file, "A", 500)
    ttl_mod.set_ttl(vault_file, "B", 1000)
    result = runner.invoke(ttl, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output
