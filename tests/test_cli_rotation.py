"""Integration-style tests for rotation CLI commands."""
from __future__ import annotations

import datetime
import json
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from envault.cli_rotation import rotate, rotation_info, stale_keys
from envault.rotation import ROTATION_META_KEY


def _vault_with_store(store: dict):
    vault = MagicMock()
    vault.get.side_effect = lambda k: store[k]
    vault.set.side_effect = lambda k, v: store.update({k: v})
    return vault


def test_rotate_command():
    runner = CliRunner()
    store = {}
    vault = _vault_with_store(store)
    with patch("envault.cli_rotation._get_vault", return_value=vault):
        result = runner.invoke(rotate, ["MY_KEY", "new_val", "--password", "pass"])
    assert result.exit_code == 0
    assert "Rotated 'MY_KEY'" in result.output


def test_rotation_info_command_no_record():
    runner = CliRunner()
    store = {}
    vault = _vault_with_store(store)
    with patch("envault.cli_rotation._get_vault", return_value=vault):
        result = runner.invoke(rotation_info, ["MY_KEY", "--password", "pass"])
    assert result.exit_code == 0
    assert "No rotation record" in result.output


def test_rotation_info_command_with_record():
    runner = CliRunner()
    ts = datetime.datetime.utcnow().isoformat()
    store = {ROTATION_META_KEY: json.dumps({"MY_KEY": ts})}
    vault = _vault_with_store(store)
    with patch("envault.cli_rotation._get_vault", return_value=vault):
        result = runner.invoke(rotation_info, ["MY_KEY", "--password", "pass"])
    assert result.exit_code == 0
    assert "last rotated at" in result.output


def test_stale_keys_command_none():
    runner = CliRunner()
    store = {}
    vault = _vault_with_store(store)
    with patch("envault.cli_rotation._get_vault", return_value=vault):
        result = runner.invoke(stale_keys, ["--days", "90", "--password", "pass"])
    assert result.exit_code == 0
    assert "All keys rotated" in result.output
