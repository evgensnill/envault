"""Lint vault keys and values for common issues."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from envault.vault import Vault

_VALID_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')


@dataclass
class LintIssue:
    key: str
    level: str  # 'error' | 'warning'
    message: str


def lint_vault(vault: Vault) -> List[LintIssue]:
    """Return a list of lint issues found in *vault*."""
    issues: List[LintIssue] = []
    keys = vault.list_keys()

    for key in keys:
        # Key naming convention
        if not _VALID_KEY_RE.match(key):
            issues.append(LintIssue(
                key=key,
                level='warning',
                message=f"Key '{key}' does not follow UPPER_SNAKE_CASE convention.",
            ))

        value: str = vault.get(key)

        # Empty value
        if value == '':
            issues.append(LintIssue(
                key=key,
                level='warning',
                message=f"Key '{key}' has an empty value.",
            ))
            continue

        # Possible plaintext secret patterns
        if re.search(r'(?i)(password|secret|token|key)s?$', key):
            if len(value) < 8:
                issues.append(LintIssue(
                    key=key,
                    level='error',
                    message=f"Key '{key}' looks like a secret but value is suspiciously short.",
                ))

        # Whitespace padding
        if value != value.strip():
            issues.append(LintIssue(
                key=key,
                level='warning',
                message=f"Key '{key}' value has leading or trailing whitespace.",
            ))

    return issues
