"""Tests for envault.rating."""
from __future__ import annotations

import json
import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.rating import (
    _entropy,
    _grade,
    rate_key,
    rate_vault,
    save_rating,
    get_saved_rating,
    RatingResult,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

class _FakeVault:
    def __init__(self, store: dict):
        self._store = store

    def list_keys(self):
        return list(self._store.keys())

    def get(self, key):
        if key not in self._store:
            raise KeyError(key)
        return self._store[key]


# ---------------------------------------------------------------------------
# unit tests
# ---------------------------------------------------------------------------

def test_entropy_empty_string():
    assert _entropy("") == 0.0


def test_entropy_uniform():
    # All same chars → 0 bits
    assert _entropy("aaaa") == 0.0


def test_entropy_two_chars():
    val = _entropy("ab")
    assert abs(val - 1.0) < 1e-9


def test_grade_boundaries():
    assert _grade(100) == "A"
    assert _grade(90) == "A"
    assert _grade(89) == "B"
    assert _grade(75) == "B"
    assert _grade(74) == "C"
    assert _grade(60) == "C"
    assert _grade(59) == "D"
    assert _grade(40) == "D"
    assert _grade(39) == "F"


def test_rate_key_short_low_entropy(tmp_path):
    vp = str(tmp_path / "vault.db")
    with patch("envault.rating.last_rotated", return_value=None):
        result = rate_key(vp, "SECRET", "abc")
    assert result.key == "SECRET"
    assert result.score < 50
    assert result.length_ok is False
    assert result.freshness_ok is False


def test_rate_key_long_high_entropy(tmp_path):
    vp = str(tmp_path / "vault.db")
    value = "aB3$xZ9!mQ2#nR7@pL5^wK8&yT1*uV4%"
    now = datetime.datetime.utcnow()
    with patch("envault.rating.last_rotated", return_value=now):
        result = rate_key(vp, "API_KEY", value)
    assert result.score >= 70
    assert result.length_ok is True
    assert result.freshness_ok is True


def test_rate_vault_returns_one_per_key(tmp_path):
    vp = str(tmp_path / "vault.db")
    vault = _FakeVault({"A": "short", "B": "x" * 40})
    with patch("envault.rating.last_rotated", return_value=None):
        results = rate_vault(vp, vault)
    assert len(results) == 2
    keys = {r.key for r in results}
    assert keys == {"A", "B"}


def test_save_and_get_rating(tmp_path):
    vp = str(tmp_path / "vault.db")
    r = RatingResult(
        key="MY_KEY",
        score=82,
        grade="B",
        entropy_bits=4.1,
        length_ok=True,
        freshness_ok=False,
    )
    save_rating(vp, r)
    stored = get_saved_rating(vp, "MY_KEY")
    assert stored is not None
    assert stored["score"] == 82
    assert stored["grade"] == "B"
    assert stored["length_ok"] is True


def test_get_saved_rating_missing_key_returns_none(tmp_path):
    vp = str(tmp_path / "vault.db")
    assert get_saved_rating(vp, "GHOST") is None


def test_save_rating_persists_to_file(tmp_path):
    vp = str(tmp_path / "vault.db")
    r = RatingResult("K", 55, "C", 3.2, False, False)
    save_rating(vp, r)
    rating_file = tmp_path / "vault.ratings.json"
    assert rating_file.exists()
    data = json.loads(rating_file.read_text())
    assert "K" in data
