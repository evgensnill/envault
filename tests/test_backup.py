"""Tests for envault.backup."""
from __future__ import annotations

import tarfile
from pathlib import Path

import pytest

from envault.backup import create_backup, list_backups, restore_backup


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    v = tmp_path / "vault.db"
    v.write_text("fake vault data")
    return v


def test_create_backup_returns_archive(vault_file, tmp_path):
    dest = tmp_path / "backups"
    archive = create_backup(vault_file, dest)
    assert archive.exists()
    assert archive.suffix == ".gz"


def test_create_backup_with_label(vault_file, tmp_path):
    dest = tmp_path / "backups"
    archive = create_backup(vault_file, dest, label="pre-deploy")
    assert "pre-deploy" in archive.name


def test_create_backup_missing_vault(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_backup(tmp_path / "nonexistent.db", tmp_path / "backups")


def test_archive_contains_vault_and_meta(vault_file, tmp_path):
    dest = tmp_path / "backups"
    archive = create_backup(vault_file, dest)
    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()
    assert vault_file.name in names
    assert "backup_meta.json" in names


def test_list_backups_empty(tmp_path):
    assert list_backups(tmp_path / "backups") == []


def test_list_backups_returns_entries(vault_file, tmp_path):
    dest = tmp_path / "backups"
    create_backup(vault_file, dest, label="v1")
    create_backup(vault_file, dest, label="v2")
    entries = list_backups(dest)
    assert len(entries) == 2
    labels = {e["label"] for e in entries}
    assert labels == {"v1", "v2"}


def test_restore_backup(vault_file, tmp_path):
    dest = tmp_path / "backups"
    archive = create_backup(vault_file, dest)
    restore_dir = tmp_path / "restored"
    result = restore_backup(archive, restore_dir)
    assert result.exists()
    assert result.read_text() == "fake vault data"


def test_restore_no_overwrite_raises(vault_file, tmp_path):
    dest = tmp_path / "backups"
    archive = create_backup(vault_file, dest)
    restore_dir = tmp_path / "restored"
    restore_backup(archive, restore_dir)
    with pytest.raises(FileExistsError):
        restore_backup(archive, restore_dir, overwrite=False)


def test_restore_with_overwrite(vault_file, tmp_path):
    dest = tmp_path / "backups"
    archive = create_backup(vault_file, dest)
    restore_dir = tmp_path / "restored"
    restore_backup(archive, restore_dir)
    result = restore_backup(archive, restore_dir, overwrite=True)
    assert result.exists()


def test_restore_missing_archive(tmp_path):
    with pytest.raises(FileNotFoundError):
        restore_backup(tmp_path / "ghost.tar.gz", tmp_path / "out")
