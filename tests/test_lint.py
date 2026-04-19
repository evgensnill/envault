"""Tests for envault.lint."""
import pytest
from unittest.mock import MagicMock

from envault.lint import lint_vault, LintIssue


def _make_vault(data: dict):
    vault = MagicMock()
    vault.list_keys.return_value = list(data.keys())
    vault.get.side_effect = lambda k: data[k]
    return vault


def test_no_issues_for_clean_vault():
    vault = _make_vault({'DATABASE_URL': 'postgres://localhost/db', 'API_KEY': 'supersecretvalue'})
    issues = lint_vault(vault)
    assert issues == []


def test_warns_on_lowercase_key():
    vault = _make_vault({'myKey': 'value'})
    issues = lint_vault(vault)
    assert any(i.key == 'myKey' and i.level == 'warning' for i in issues)


def test_warns_on_empty_value():
    vault = _make_vault({'MY_VAR': ''})
    issues = lint_vault(vault)
    assert any(i.key == 'MY_VAR' and 'empty' in i.message for i in issues)


def test_errors_on_short_secret_value():
    vault = _make_vault({'APP_SECRET': 'abc'})
    issues = lint_vault(vault)
    assert any(i.key == 'APP_SECRET' and i.level == 'error' for i in issues)


def test_no_error_for_long_secret_value():
    vault = _make_vault({'APP_SECRET': 'a-very-long-secret-value-123'})
    issues = lint_vault(vault)
    errors = [i for i in issues if i.key == 'APP_SECRET' and i.level == 'error']
    assert errors == []


def test_warns_on_whitespace_padding():
    vault = _make_vault({'MY_VAR': '  hello  '})
    issues = lint_vault(vault)
    assert any(i.key == 'MY_VAR' and 'whitespace' in i.message for i in issues)


def test_empty_vault_returns_no_issues():
    vault = _make_vault({})
    assert lint_vault(vault) == []


def test_multiple_issues_on_same_key():
    # lowercase key AND whitespace padding
    vault = _make_vault({'badKey': '  val  '})
    issues = lint_vault(vault)
    keys_reported = [i.key for i in issues]
    assert keys_reported.count('badKey') >= 2
