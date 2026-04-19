"""Tests for envault.hooks."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.hooks import add_hook, remove_hook, load_hooks, run_hooks


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.db"


def test_load_hooks_no_file_returns_empty(vault_path):
    assert load_hooks(vault_path) == {}


def test_add_hook_creates_entry(vault_path):
    add_hook(vault_path, "post-set", "echo hello")
    hooks = load_hooks(vault_path)
    assert "echo hello" in hooks["post-set"]


def test_add_hook_idempotent(vault_path):
    add_hook(vault_path, "post-set", "echo hello")
    add_hook(vault_path, "post-set", "echo hello")
    assert load_hooks(vault_path)["post-set"].count("echo hello") == 1


def test_add_hook_invalid_event_raises(vault_path):
    with pytest.raises(ValueError, match="Unknown event"):
        add_hook(vault_path, "on-explode", "rm -rf /")


def test_remove_hook_returns_true(vault_path):
    add_hook(vault_path, "pre-set", "echo before")
    result = remove_hook(vault_path, "pre-set", "echo before")
    assert result is True
    assert "echo before" not in load_hooks(vault_path).get("pre-set", [])


def test_remove_hook_missing_returns_false(vault_path):
    result = remove_hook(vault_path, "pre-set", "echo nothing")
    assert result is False


def test_multiple_hooks_same_event(vault_path):
    add_hook(vault_path, "post-rotate", "echo a")
    add_hook(vault_path, "post-rotate", "echo b")
    cmds = load_hooks(vault_path)["post-rotate"]
    assert cmds == ["echo a", "echo b"]


def test_run_hooks_executes_command(vault_path):
    add_hook(vault_path, "post-set", "echo ran")
    outputs = run_hooks(vault_path, "post-set")
    assert outputs == ["ran"]


def test_run_hooks_no_hooks_returns_empty(vault_path):
    outputs = run_hooks(vault_path, "post-set")
    assert outputs == []
