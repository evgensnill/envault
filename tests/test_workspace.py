"""Tests for envault.workspace and envault.cli_workspace."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_workspace import workspace
import envault.workspace as ws_mod


@pytest.fixture(autouse=True)
def isolated_workspaces(tmp_path, monkeypatch):
    ws_file = tmp_path / ".envault" / "workspaces.json"
    monkeypatch.setattr(ws_mod, "_WORKSPACES_FILE", ws_file)
    yield ws_file


# --- unit tests ---

def test_add_and_get_workspace():
    ws_mod.add_workspace("prod", "/vaults/prod.vault")
    meta = ws_mod.get_workspace("prod")
    assert meta["vault_path"] == "/vaults/prod.vault"
    assert meta["description"] == ""


def test_add_workspace_with_description():
    ws_mod.add_workspace("staging", "/vaults/staging.vault", description="Staging env")
    assert ws_mod.get_workspace("staging")["description"] == "Staging env"


def test_get_missing_workspace_raises():
    with pytest.raises(KeyError, match="not found"):
        ws_mod.get_workspace("ghost")


def test_remove_workspace():
    ws_mod.add_workspace("temp", "/tmp/temp.vault")
    ws_mod.remove_workspace("temp")
    assert "temp" not in ws_mod.list_workspaces()


def test_remove_missing_workspace_raises():
    with pytest.raises(KeyError):
        ws_mod.remove_workspace("nonexistent")


def test_list_workspaces_sorted():
    ws_mod.add_workspace("zebra", "/z")
    ws_mod.add_workspace("alpha", "/a")
    assert ws_mod.list_workspaces() == ["alpha", "zebra"]


def test_set_and_get_active_workspace():
    ws_mod.add_workspace("dev", "/dev.vault")
    ws_mod.add_workspace("prod", "/prod.vault")
    ws_mod.set_active_workspace("dev")
    assert ws_mod.get_active_workspace() == "dev"
    ws_mod.set_active_workspace("prod")
    assert ws_mod.get_active_workspace() == "prod"


def test_get_active_workspace_none_when_empty():
    assert ws_mod.get_active_workspace() is None


def test_set_active_missing_raises():
    with pytest.raises(KeyError):
        ws_mod.set_active_workspace("missing")


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_add_and_list(runner):
    result = runner.invoke(workspace, ["add", "myapp", "/vaults/myapp.vault", "-d", "Main app"])
    assert result.exit_code == 0
    assert "myapp" in result.output

    result = runner.invoke(workspace, ["list"])
    assert "myapp" in result.output
    assert "/vaults/myapp.vault" in result.output
    assert "Main app" in result.output


def test_cli_list_empty(runner):
    result = runner.invoke(workspace, ["list"])
    assert result.exit_code == 0
    assert "No workspaces" in result.output


def test_cli_remove(runner):
    runner.invoke(workspace, ["add", "tmp", "/tmp.vault"])
    result = runner.invoke(workspace, ["remove", "tmp"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_use_and_current(runner):
    runner.invoke(workspace, ["add", "live", "/live.vault"])
    runner.invoke(workspace, ["use", "live"])
    result = runner.invoke(workspace, ["current"])
    assert "live" in result.output


def test_cli_use_missing_fails(runner):
    result = runner.invoke(workspace, ["use", "ghost"])
    assert result.exit_code != 0
