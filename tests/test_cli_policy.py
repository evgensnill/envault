"""Tests for CLI policy commands."""
import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock
from envault.cli_policy import policy
from envault.policy import PolicyRule, PolicyViolation


def _runner():
    return CliRunner()


def test_list_no_rules(tmp_path):
    runner = _runner()
    with runner.isolated_filesystem():
        result = runner.invoke(policy, ["list", "--vault", ".envault"])
        assert result.exit_code == 0
        assert "No rules defined" in result.output


def test_add_rule_and_list(tmp_path):
    runner = _runner()
    with runner.isolated_filesystem():
        result = runner.invoke(policy, [
            "add-rule", "API_KEY", "--vault", ".envault",
            "--required", "--min-length", "8"
        ])
        assert result.exit_code == 0
        assert "API_KEY" in result.output

        result = runner.invoke(policy, ["list", "--vault", ".envault"])
        assert "API_KEY" in result.output
        assert "required" in result.output
        assert "min_length=8" in result.output


def test_check_passes(tmp_path):
    runner = _runner()
    fake_vault = MagicMock()
    fake_vault.list_keys.return_value = ["API_KEY"]
    fake_vault.get.return_value = "supersecretvalue"
    with runner.isolated_filesystem():
        policy_data = {"rules": [{"key": "API_KEY", "required": True, "min_length": 8}]}
        Path(".envault-policy.json").write_text(json.dumps(policy_data))
        with patch("envault.cli_policy._get_vault", return_value=fake_vault):
            result = runner.invoke(policy, ["check", "--vault", ".envault", "--password", "pw"])
        assert result.exit_code == 0
        assert "passed" in result.output


def test_check_fails_on_violation(tmp_path):
    runner = _runner()
    fake_vault = MagicMock()
    fake_vault.list_keys.return_value = []
    with runner.isolated_filesystem():
        policy_data = {"rules": [{"key": "API_KEY", "required": True}]}
        Path(".envault-policy.json").write_text(json.dumps(policy_data))
        with patch("envault.cli_policy._get_vault", return_value=fake_vault):
            result = runner.invoke(policy, ["check", "--vault", ".envault", "--password", "pw"])
        assert result.exit_code == 1
        assert "required" in result.output
