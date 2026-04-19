"""CLI tests for backup commands."""
from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from envault.cli_backup import backup


def _runner():
    return CliRunner(mix_stderr=False)


def test_create_command(tmp_path):
    vault = tmp_path / "vault.db"
    vault.write_text("data")
    dest = tmp_path / "backups"
    result = _runner().invoke(backup, ["create", "--vault", str(vault), "--dest", str(dest)])
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_create_command_missing_vault(tmp_path):
    result = _runner().invoke(
        backup, ["create", "--vault", str(tmp_path / "nope.db"), "--dest", str(tmp_path)]
    )
    assert result.exit_code == 1


def test_list_command_empty(tmp_path):
    result = _runner().invoke(backup, ["list", "--dest", str(tmp_path / "backups")])
    assert result.exit_code == 0
    assert "No backups found" in result.output


def test_list_command_with_entries(tmp_path):
    vault = tmp_path / "vault.db"
    vault.write_text("data")
    dest = tmp_path / "backups"
    _runner().invoke(backup, ["create", "--vault", str(vault), "--dest", str(dest), "--label", "test"])
    result = _runner().invoke(backup, ["list", "--dest", str(dest)])
    assert result.exit_code == 0
    assert "test" in result.output


def test_restore_command(tmp_path):
    vault = tmp_path / "vault.db"
    vault.write_text("data")
    dest = tmp_path / "backups"
    r = _runner().invoke(backup, ["create", "--vault", str(vault), "--dest", str(dest)])
    archive = r.output.split("Backup created: ")[1].strip()
    out_dir = tmp_path / "out"
    result = _runner().invoke(backup, ["restore", archive, "--dest", str(out_dir)])
    assert result.exit_code == 0
    assert "restored to" in result.output


def test_restore_command_no_overwrite(tmp_path):
    vault = tmp_path / "vault.db"
    vault.write_text("data")
    dest = tmp_path / "backups"
    r = _runner().invoke(backup, ["create", "--vault", str(vault), "--dest", str(dest)])
    archive = r.output.split("Backup created: ")[1].strip()
    out_dir = tmp_path / "out"
    _runner().invoke(backup, ["restore", archive, "--dest", str(out_dir)])
    result = _runner().invoke(backup, ["restore", archive, "--dest", str(out_dir)])
    assert result.exit_code == 1
