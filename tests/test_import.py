"""Tests for envault.import_ module."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from envault.import_ import _parse_dotenv, _parse_json, import_vault
from envault.vault import Vault


def _make_vault(tmp_path: Path, password: str = "test") -> Vault:
    v = Vault(tmp_path / "vault.enc", password)
    v.save()
    return v


# --- unit tests for parsers ---

def test_parse_dotenv_basic():
    text = textwrap.dedent("""
        # comment
        KEY1=value1
        KEY2 = value2
        KEY3="quoted value"
        KEY4='single'
    """)
    result = _parse_dotenv(text)
    assert result == {
        "KEY1": "value1",
        "KEY2": "value2",
        "KEY3": "quoted value",
        "KEY4": "single",
    }


def test_parse_dotenv_skips_blank_and_comments():
    result = _parse_dotenv("# only comments\n\n")
    assert result == {}


def test_parse_json_basic():
    data = {"A": "1", "B": "hello"}
    result = _parse_json(json.dumps(data))
    assert result == data


def test_parse_json_non_dict_raises():
    with pytest.raises(ValueError, match="top-level object"):
        _parse_json(json.dumps(["a", "b"]))


# --- integration tests for import_vault ---

def test_import_dotenv(tmp_path: Path):
    vault = _make_vault(tmp_path)
    src = tmp_path / ".env"
    src.write_text("FOO=bar\nBAZ=qux\n")
    imported, skipped = import_vault(vault, src, fmt="dotenv")
    assert imported == 2
    assert skipped == 0
    assert vault.get("FOO") == "bar"
    assert vault.get("BAZ") == "qux"


def test_import_json(tmp_path: Path):
    vault = _make_vault(tmp_path)
    src = tmp_path / "secrets.json"
    src.write_text(json.dumps({"TOKEN": "abc123"}))
    imported, skipped = import_vault(vault, src, fmt="json")
    assert imported == 1
    assert vault.get("TOKEN") == "abc123"


def test_import_skips_existing_without_overwrite(tmp_path: Path):
    vault = _make_vault(tmp_path)
    vault.set("EXISTING", "original")
    vault.save()
    src = tmp_path / ".env"
    src.write_text("EXISTING=new\nNEW_KEY=val\n")
    imported, skipped = import_vault(vault, src, fmt="dotenv", overwrite=False)
    assert imported == 1
    assert skipped == 1
    assert vault.get("EXISTING") == "original"


def test_import_overwrite(tmp_path: Path):
    vault = _make_vault(tmp_path)
    vault.set("KEY", "old")
    vault.save()
    src = tmp_path / ".env"
    src.write_text("KEY=new\n")
    imported, skipped = import_vault(vault, src, fmt="dotenv", overwrite=True)
    assert imported == 1
    assert skipped == 0
    assert vault.get("KEY") == "new"


def test_import_unsupported_format_raises(tmp_path: Path):
    vault = _make_vault(tmp_path)
    src = tmp_path / "f.xml"
    src.write_text("<key>val</key>")
    with pytest.raises(ValueError, match="Unsupported import format"):
        import_vault(vault, src, fmt="xml")
