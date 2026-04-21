"""Tests for envault.namespace."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.vault import Vault
from envault import namespace as ns_mod
from envault.cli_namespace import namespace as namespace_cli


def _make_vault(tmp_path: Path, password: str = "pass") -> str:
    vault_file = str(tmp_path / "test.vault")
    v = Vault(vault_file)
    v.load(password)
    v.set("API_KEY", "secret1", password)
    v.set("DB_PASSWORD", "secret2", password)
    v.set("CACHE_URL", "redis://localhost", password)
    v.save(password)
    return vault_file


def test_assign_and_get_namespace(tmp_path):
    vp = _make_vault(tmp_path)
    ns_mod.assign_namespace(vp, "API_KEY", "auth")
    assert ns_mod.get_namespace(vp, "API_KEY") == "auth"


def test_get_namespace_unassigned_returns_none(tmp_path):
    vp = _make_vault(tmp_path)
    assert ns_mod.get_namespace(vp, "API_KEY") is None


def test_assign_missing_key_raises(tmp_path):
    vp = _make_vault(tmp_path)
    with pytest.raises(KeyError, match="MISSING"):
        ns_mod.assign_namespace(vp, "MISSING", "auth")


def test_assign_invalid_namespace_raises(tmp_path):
    vp = _make_vault(tmp_path)
    with pytest.raises(ValueError, match="not a valid identifier"):
        ns_mod.assign_namespace(vp, "API_KEY", "my-ns")


def test_remove_namespace_returns_true(tmp_path):
    vp = _make_vault(tmp_path)
    ns_mod.assign_namespace(vp, "API_KEY", "auth")
    assert ns_mod.remove_namespace(vp, "API_KEY") is True
    assert ns_mod.get_namespace(vp, "API_KEY") is None


def test_remove_missing_namespace_returns_false(tmp_path):
    vp = _make_vault(tmp_path)
    assert ns_mod.remove_namespace(vp, "API_KEY") is False


def test_keys_in_namespace(tmp_path):
    vp = _make_vault(tmp_path)
    ns_mod.assign_namespace(vp, "API_KEY", "auth")
    ns_mod.assign_namespace(vp, "DB_PASSWORD", "database")
    ns_mod.assign_namespace(vp, "CACHE_URL", "database")
    assert ns_mod.keys_in_namespace(vp, "database") == ["DB_PASSWORD", "CACHE_URL"]
    assert ns_mod.keys_in_namespace(vp, "auth") == ["API_KEY"]


def test_list_namespaces(tmp_path):
    vp = _make_vault(tmp_path)
    ns_mod.assign_namespace(vp, "API_KEY", "auth")
    ns_mod.assign_namespace(vp, "DB_PASSWORD", "database")
    mapping = ns_mod.list_namespaces(vp)
    assert set(mapping.keys()) == {"auth", "database"}
    assert mapping["auth"] == ["API_KEY"]


def test_cli_assign_and_list(tmp_path):
    vp = _make_vault(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        namespace_cli,
        ["assign", "API_KEY", "auth", "--vault", vp, "--password", "pass"],
    )
    assert result.exit_code == 0
    assert "Assigned 'API_KEY' to namespace 'auth'" in result.output

    result = runner.invoke(
        namespace_cli,
        ["list", "--vault", vp, "--password", "pass"],
    )
    assert result.exit_code == 0
    assert "auth" in result.output
    assert "API_KEY" in result.output


def test_cli_list_empty(tmp_path):
    vp = _make_vault(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        namespace_cli,
        ["list", "--vault", vp, "--password", "pass"],
    )
    assert result.exit_code == 0
    assert "No namespace assignments" in result.output
