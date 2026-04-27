"""Tests for envault.note."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envault.note import set_note, get_note, remove_note, list_notes, _note_path


@pytest.fixture()
def vault_path(tmp_path: Path) -> str:
    p = tmp_path / "vault.env"
    p.write_text("{}")  # minimal vault file
    return str(p)


VAULT_KEYS = ["DB_URL", "API_KEY", "SECRET"]


def test_set_and_get_note(vault_path):
    set_note(vault_path, "DB_URL", "Primary database connection string.", VAULT_KEYS)
    record = get_note(vault_path, "DB_URL")
    assert record is not None
    assert record["text"] == "Primary database connection string."
    assert "updated_at" in record


def test_get_note_missing_key_returns_none(vault_path):
    assert get_note(vault_path, "DB_URL") is None


def test_set_note_missing_vault_key_raises(vault_path):
    with pytest.raises(KeyError, match="MISSING_KEY"):
        set_note(vault_path, "MISSING_KEY", "some note", VAULT_KEYS)


def test_set_note_empty_text_raises(vault_path):
    with pytest.raises(ValueError, match="empty"):
        set_note(vault_path, "DB_URL", "", VAULT_KEYS)


def test_remove_note_returns_true(vault_path):
    set_note(vault_path, "API_KEY", "Third-party API key.", VAULT_KEYS)
    assert remove_note(vault_path, "API_KEY") is True
    assert get_note(vault_path, "API_KEY") is None


def test_remove_note_missing_returns_false(vault_path):
    assert remove_note(vault_path, "API_KEY") is False


def test_list_notes_empty(vault_path):
    assert list_notes(vault_path) == {}


def test_list_notes_returns_all(vault_path):
    set_note(vault_path, "DB_URL", "DB note.", VAULT_KEYS)
    set_note(vault_path, "API_KEY", "API note.", VAULT_KEYS)
    notes = list_notes(vault_path)
    assert set(notes.keys()) == {"DB_URL", "API_KEY"}


def test_note_file_is_valid_json(vault_path):
    set_note(vault_path, "SECRET", "Master secret.", VAULT_KEYS)
    raw = _note_path(vault_path).read_text()
    parsed = json.loads(raw)
    assert "SECRET" in parsed


def test_overwrite_note(vault_path):
    set_note(vault_path, "DB_URL", "First note.", VAULT_KEYS)
    set_note(vault_path, "DB_URL", "Updated note.", VAULT_KEYS)
    record = get_note(vault_path, "DB_URL")
    assert record["text"] == "Updated note."
