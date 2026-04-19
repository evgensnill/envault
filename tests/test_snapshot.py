"""Tests for envault.snapshot."""
import time
from pathlib import Path

import pytest

from envault.vault import Vault
from envault.snapshot import (
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
    save_snapshot,
)


def _make_vault(tmp_path: Path, secrets: dict) -> Vault:
    path = str(tmp_path / "vault.db")
    v = Vault(path, "testpass")
    v.load()
    for k, val in secrets.items():
        v.set(k, val)
    v.save()
    return v


def test_save_snapshot_returns_id(tmp_path):
    v = _make_vault(tmp_path, {"KEY": "value"})
    snap_id = save_snapshot(v)
    assert snap_id
    snap_file = tmp_path / ".snapshots" / f"{snap_id}.json"
    assert snap_file.exists()


def test_save_snapshot_with_label(tmp_path):
    v = _make_vault(tmp_path, {"A": "1"})
    snap_id = save_snapshot(v, label="before-deploy")
    assert "before-deploy" in snap_id


def test_list_snapshots_empty(tmp_path):
    v = _make_vault(tmp_path, {})
    assert list_snapshots(v) == []


def test_list_snapshots_returns_metadata(tmp_path):
    v = _make_vault(tmp_path, {"X": "y"})
    save_snapshot(v, label="s1")
    time.sleep(0.01)
    save_snapshot(v)
    snaps = list_snapshots(v)
    assert len(snaps) == 2
    assert all("snap_id" in s for s in snaps)


def test_restore_snapshot_overwrites(tmp_path):
    v = _make_vault(tmp_path, {"FOO": "original"})
    snap_id = save_snapshot(v)
    v.set("FOO", "changed")
    v.save()
    restored = restore_snapshot(v, snap_id, overwrite=True)
    assert "FOO" in restored
    assert v.get("FOO") == "original"


def test_restore_snapshot_no_overwrite(tmp_path):
    v = _make_vault(tmp_path, {"FOO": "original"})
    snap_id = save_snapshot(v)
    v.set("FOO", "changed")
    v.save()
    restored = restore_snapshot(v, snap_id, overwrite=False)
    assert "FOO" not in restored
    assert v.get("FOO") == "changed"


def test_restore_missing_snapshot_raises(tmp_path):
    v = _make_vault(tmp_path, {})
    with pytest.raises(FileNotFoundError):
        restore_snapshot(v, "nonexistent_snap")


def test_delete_snapshot(tmp_path):
    v = _make_vault(tmp_path, {"K": "v"})
    snap_id = save_snapshot(v)
    delete_snapshot(v, snap_id)
    assert list_snapshots(v) == []


def test_delete_missing_snapshot_raises(tmp_path):
    v = _make_vault(tmp_path, {})
    with pytest.raises(FileNotFoundError):
        delete_snapshot(v, "ghost")
