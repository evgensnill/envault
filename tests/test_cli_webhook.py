"""Tests for envault.cli_webhook."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.cli_webhook import webhook
from envault import webhook as wh


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.env"
    p.write_text("{}")
    return str(p)


def _fake_vault(vault_path):
    v = MagicMock()
    v.path = vault_path
    return v


def test_add_and_list(runner, vault_path):
    with patch("envault.cli_webhook._get_vault", return_value=_fake_vault(vault_path)):
        result = runner.invoke(webhook, ["add", "myslack", "https://hooks.example.com", "--events", "set,rotate"])
    assert result.exit_code == 0
    assert "myslack" in result.output

    with patch("envault.cli_webhook._get_vault", return_value=_fake_vault(vault_path)):
        result = runner.invoke(webhook, ["list"])
    assert result.exit_code == 0
    assert "myslack" in result.output
    assert "https://hooks.example.com" in result.output


def test_add_invalid_event(runner, vault_path):
    with patch("envault.cli_webhook._get_vault", return_value=_fake_vault(vault_path)):
        result = runner.invoke(webhook, ["add", "bad", "https://example.com", "--events", "invalid_event"])
    assert result.exit_code != 0
    assert "Invalid events" in result.output


def test_remove_existing(runner, vault_path):
    wh.add_webhook(vault_path, "to_remove", "https://example.com", ["set"])
    with patch("envault.cli_webhook._get_vault", return_value=_fake_vault(vault_path)):
        result = runner.invoke(webhook, ["remove", "to_remove"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing(runner, vault_path):
    with patch("envault.cli_webhook._get_vault", return_value=_fake_vault(vault_path)):
        result = runner.invoke(webhook, ["remove", "ghost"])
    assert result.exit_code != 0


def test_list_empty(runner, vault_path):
    with patch("envault.cli_webhook._get_vault", return_value=_fake_vault(vault_path)):
        result = runner.invoke(webhook, ["list"])
    assert result.exit_code == 0
    assert "No webhooks" in result.output


def test_fire_cmd(runner, vault_path):
    wh.add_webhook(vault_path, "h1", "https://example.com", ["set"])
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    with patch("envault.cli_webhook._get_vault", return_value=_fake_vault(vault_path)), \
         patch("urllib.request.urlopen", return_value=mock_ctx):
        result = runner.invoke(webhook, ["fire", "set", "--key", "MY_KEY"])
    assert result.exit_code == 0
    assert "OK" in result.output
