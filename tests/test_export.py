"""Tests for envault.export and the export CLI command."""
from __future__ import annotations
import json
import os
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.vault import Vault
from envault.export import export_vault, _to_dotenv, _to_json, _to_shell
from envault.cli_export import export

PASSWORD = "test-pass"


def _make_vault(tmp_path, data: dict[str, str]) -> Vault:
    path = str(tmp_path / "vault")
    v = Vault(path, PASSWORD)
    for k, val in data.items():
        v.set(k, val)
    v.save()
    return v


def test_dotenv_format(tmp_path):
    v = _make_vault(tmp_path, {"FOO": "bar", "BAZ": 'qu"x'})
    out = export_vault(v, fmt="dotenv")
    assert 'BAZ="qu\\"x"' in out
    assert 'FOO="bar"' in out


def test_json_format(tmp_path):
    v = _make_vault(tmp_path, {"KEY": "value"})
    out = export_vault(v, fmt="json")
    parsed = json.loads(out)
    assert parsed == {"KEY": "value"}


def test_shell_format(tmp_path):
    v = _make_vault(tmp_path, {"MY_VAR": "it's alive"})
    out = export_vault(v, fmt="shell")
    assert "export MY_VAR=" in out
    assert "it'\"'\"'s alive" in out


def test_empty_vault(tmp_path):
    v = _make_vault(tmp_path, {})
    for fmt in ("dotenv", "json", "shell"):
        out = export_vault(v, fmt=fmt)  # type: ignore[arg-type]
        assert isinstance(out, str)


def test_cli_export_stdout(tmp_path):
    v = _make_vault(tmp_path, {"HELLO": "world"})
    runner = CliRunner()
    with patch("envault.cli_export._get_vault", return_value=v):
        result = runner.invoke(
            export,
            ["--format", "json", "--password", PASSWORD],
        )
    assert result.exit_code == 0
    assert json.loads(result.output)["HELLO"] == "world"


def test_cli_export_to_file(tmp_path):
    v = _make_vault(tmp_path, {"A": "1"})
    out_file = str(tmp_path / "out.env")
    runner = CliRunner()
    with patch("envault.cli_export._get_vault", return_value=v):
        result = runner.invoke(
            export,
            ["--format", "dotenv", "--output", out_file, "--password", PASSWORD],
        )
    assert result.exit_code == 0
    assert os.path.exists(out_file)
    content = open(out_file).read()
    assert 'A="1"' in content
