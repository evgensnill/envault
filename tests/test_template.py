"""Tests for envault.template."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.template import render_string, render_file


class _FakeVault:
    """Minimal vault stub for testing."""

    def __init__(self, data: dict[str, str]):
        self._data = data

    def get(self, key: str) -> str:
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]


def test_render_string_basic():
    vault = _FakeVault({"DB_HOST": "localhost", "DB_PORT": "5432"})
    tmpl = "host={{ DB_HOST }} port={{DB_PORT}}"
    result, missing = render_string(tmpl, vault)
    assert result == "host=localhost port=5432"
    assert missing == []


def test_render_string_missing_key():
    vault = _FakeVault({"A": "1"})
    tmpl = "{{A}} and {{B}}"
    result, missing = render_string(tmpl, vault)
    assert "1" in result
    assert "{{B}}" in result  # placeholder left intact
    assert missing == ["B"]


def test_render_string_no_placeholders():
    vault = _FakeVault({})
    tmpl = "no placeholders here"
    result, missing = render_string(tmpl, vault)
    assert result == tmpl
    assert missing == []


def test_render_string_whitespace_in_placeholder():
    vault = _FakeVault({"MY_KEY": "value"})
    result, missing = render_string("{{ MY_KEY }}", vault)
    assert result == "value"
    assert missing == []


def test_render_file_writes_output(tmp_path: Path):
    vault = _FakeVault({"SECRET": "s3cr3t"})
    src = tmp_path / "tmpl.txt"
    src.write_text("pass={{SECRET}}")
    dest = tmp_path / "out.txt"
    rendered, missing = render_file(src, vault, dest=dest)
    assert rendered == "pass=s3cr3t"
    assert dest.read_text() == "pass=s3cr3t"
    assert missing == []


def test_render_file_no_dest(tmp_path: Path):
    vault = _FakeVault({"X": "42"})
    src = tmp_path / "tmpl.txt"
    src.write_text("x={{X}}")
    rendered, missing = render_file(src, vault, dest=None)
    assert rendered == "x=42"
    assert missing == []


def test_render_file_missing_keys(tmp_path: Path):
    vault = _FakeVault({})
    src = tmp_path / "tmpl.txt"
    src.write_text("{{MISSING}}")
    rendered, missing = render_file(src, vault)
    assert "{{MISSING}}" in rendered
    assert "MISSING" in missing
