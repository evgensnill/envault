"""Tests for envault.cli_profile CLI commands."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envault.cli_profile import profile
from envault import profile as prof


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(prof, "_PROFILES_FILE", tmp_path / "profiles.json")


def test_add_and_list(runner):
    result = runner.invoke(profile, ["add", "dev", "/tmp/dev.vault"])
    assert result.exit_code == 0
    assert "added" in result.output

    result = runner.invoke(profile, ["list"])
    assert "dev" in result.output
    assert "/tmp/dev.vault" in result.output


def test_list_empty(runner):
    result = runner.invoke(profile, ["list"])
    assert "No profiles" in result.output


def test_remove(runner):
    runner.invoke(profile, ["add", "dev", "/tmp/dev.vault"])
    result = runner.invoke(profile, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing(runner):
    result = runner.invoke(profile, ["remove", "ghost"])
    assert result.exit_code != 0


def test_use_sets_default(runner):
    runner.invoke(profile, ["add", "prod", "/prod"])
    result = runner.invoke(profile, ["use", "prod"])
    assert result.exit_code == 0
    assert "prod" in result.output

    result = runner.invoke(profile, ["list"])
    assert "(default)" in result.output


def test_show(runner):
    runner.invoke(profile, ["add", "dev", "/tmp/dev.vault", "-d", "Dev env"])
    result = runner.invoke(profile, ["show", "dev"])
    assert result.exit_code == 0
    assert "/tmp/dev.vault" in result.output
    assert "Dev env" in result.output


def test_show_missing(runner):
    result = runner.invoke(profile, ["show", "ghost"])
    assert result.exit_code != 0
