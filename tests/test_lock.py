"""Tests for envault.lock."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.lock import (
    acquire_lock,
    is_locked,
    lock_info,
    release_lock,
)
from envault.cli_lock import lock


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    p.write_text("{}")
    return p


# --- unit tests ---

def test_acquire_creates_lock_file(vault_path):
    acquire_lock(vault_path)
    assert vault_path.with_suffix(".lock").exists()
    release_lock(vault_path)


def test_is_locked_after_acquire(vault_path):
    assert not is_locked(vault_path)
    acquire_lock(vault_path)
    assert is_locked(vault_path)
    release_lock(vault_path)


def test_release_removes_lock_file(vault_path):
    acquire_lock(vault_path)
    release_lock(vault_path)
    assert not is_locked(vault_path)


def test_release_no_op_when_not_locked(vault_path):
    release_lock(vault_path)  # should not raise


def test_lock_info_contains_pid_and_timestamp(vault_path):
    before = time.time()
    acquire_lock(vault_path)
    info = lock_info(vault_path)
    after = time.time()
    assert info is not None
    assert info["pid"] == os.getpid()
    assert before <= info["acquired_at"] <= after
    release_lock(vault_path)


def test_lock_info_returns_none_when_not_locked(vault_path):
    assert lock_info(vault_path) is None


def test_stale_lock_is_overwritten(vault_path):
    lock_file = vault_path.with_suffix(".lock")
    stale_data = {"pid": 99999, "acquired_at": time.time() - 120}
    lock_file.write_text(json.dumps(stale_data))
    # Should succeed because the lock is stale
    acquire_lock(vault_path, timeout=2.0)
    info = lock_info(vault_path)
    assert info["pid"] == os.getpid()
    release_lock(vault_path)


def test_acquire_times_out_when_locked(vault_path):
    acquire_lock(vault_path)
    try:
        with pytest.raises(RuntimeError, match="Could not acquire lock"):
            acquire_lock(vault_path, timeout=0.3)
    finally:
        release_lock(vault_path)


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_acquire_and_release(runner, vault_path):
    result = runner.invoke(lock, ["acquire", str(vault_path)])
    assert result.exit_code == 0
    assert "acquired" in result.output.lower()

    result = runner.invoke(lock, ["release", str(vault_path)])
    assert result.exit_code == 0
    assert "released" in result.output.lower()


def test_cli_status_not_locked(runner, vault_path):
    result = runner.invoke(lock, ["status", str(vault_path)])
    assert result.exit_code == 0
    assert "NOT locked" in result.output


def test_cli_status_locked(runner, vault_path):
    acquire_lock(vault_path)
    try:
        result = runner.invoke(lock, ["status", str(vault_path)])
        assert result.exit_code == 0
        assert "LOCKED" in result.output
    finally:
        release_lock(vault_path)
