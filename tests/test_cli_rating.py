"""CLI tests for envault.cli_rating."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from envault.cli_rating import rating
from envault.rating import RatingResult


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _runner():
    return CliRunner()


def _fake_vault(store: dict):
    v = MagicMock()
    v.list_keys.return_value = list(store.keys())
    v.get.side_effect = lambda k: store[k]
    return v


_SAMPLE_RESULT = RatingResult(
    key="API_KEY",
    score=78,
    grade="B",
    entropy_bits=4.5,
    length_ok=True,
    freshness_ok=True,
)


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_score_single_key(tmp_path):
    vp = str(tmp_path / "vault.db")
    vault = _fake_vault({"API_KEY": "supersecretvalue1234567890abcdef"})
    with patch("envault.cli_rating._get_vault", return_value=vault), \
         patch("envault.cli_rating.rate_key", return_value=_SAMPLE_RESULT):
        result = _runner().invoke(rating, ["score", vp, "pass", "API_KEY"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "78" in result.output


def test_score_all_keys(tmp_path):
    vp = str(tmp_path / "vault.db")
    vault = _fake_vault({"A": "val1", "B": "val2"})
    results = [
        RatingResult("A", 55, "C", 3.1, False, False),
        RatingResult("B", 80, "B", 4.8, True, True),
    ]
    with patch("envault.cli_rating._get_vault", return_value=vault), \
         patch("envault.cli_rating.rate_vault", return_value=results):
        result = _runner().invoke(rating, ["score", vp, "pass"])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output


def test_score_missing_key_exits_nonzero(tmp_path):
    vp = str(tmp_path / "vault.db")
    vault = _fake_vault({})
    vault.get.side_effect = KeyError("GHOST")
    with patch("envault.cli_rating._get_vault", return_value=vault):
        result = _runner().invoke(rating, ["score", vp, "pass", "GHOST"])
    assert result.exit_code != 0


def test_score_no_keys_empty_vault(tmp_path):
    vp = str(tmp_path / "vault.db")
    vault = _fake_vault({})
    with patch("envault.cli_rating._get_vault", return_value=vault), \
         patch("envault.cli_rating.rate_vault", return_value=[]):
        result = _runner().invoke(rating, ["score", vp, "pass"])
    assert result.exit_code == 0
    assert "No keys" in result.output


def test_summary_command(tmp_path):
    vp = str(tmp_path / "vault.db")
    vault = _fake_vault({"X": "v"})
    results = [
        RatingResult("X", 91, "A", 4.9, True, True),
    ]
    with patch("envault.cli_rating._get_vault", return_value=vault), \
         patch("envault.cli_rating.rate_vault", return_value=results):
        result = _runner().invoke(rating, ["summary", vp, "pass"])
    assert result.exit_code == 0
    assert "91" in result.output or "A" in result.output
    assert "Keys rated" in result.output
