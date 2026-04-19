"""Search and filter vault keys by pattern or metadata."""
from __future__ import annotations

import fnmatch
import re
from typing import List, Optional

from envault.vault import Vault
from envault.rotation import get_rotation_meta


def search_keys(
    vault: Vault,
    pattern: Optional[str] = None,
    *,
    regex: bool = False,
    rotated_after: Optional[str] = None,
    rotated_before: Optional[str] = None,
) -> List[str]:
    """Return vault keys matching *pattern* and optional rotation date filters.

    Args:
        vault: The Vault instance to search.
        pattern: Glob (default) or regex pattern to match key names.
        regex: If True, treat *pattern* as a regular expression.
        rotated_after: ISO-8601 date string; include only keys rotated after this date.
        rotated_before: ISO-8601 date string; include only keys rotated before this date.

    Returns:
        Sorted list of matching key names.
    """
    keys = vault.keys()

    if pattern:
        if regex:
            compiled = re.compile(pattern)
            keys = [k for k in keys if compiled.search(k)]
        else:
            keys = fnmatch.filter(keys, pattern)

    if rotated_after or rotated_before:
        filtered = []
        for key in keys:
            meta = get_rotation_meta(vault, key)
            last = meta.get("last_rotated")
            if last is None:
                continue
            if rotated_after and last <= rotated_after:
                continue
            if rotated_before and last >= rotated_before:
                continue
            filtered.append(key)
        keys = filtered

    return sorted(keys)


def grep_values(
    vault: Vault,
    pattern: str,
    *,
    regex: bool = False,
) -> List[str]:
    """Return keys whose *decrypted* value matches *pattern*.

    Args:
        vault: The Vault instance to search.
        pattern: Glob or regex pattern matched against decrypted values.
        regex: If True, treat *pattern* as a regular expression.

    Returns:
        Sorted list of matching key names.
    """
    results = []
    for key in vault.keys():
        value = vault.get(key)
        if value is None:
            continue
        if regex:
            if re.search(pattern, value):
                results.append(key)
        else:
            if fnmatch.fnmatch(value, pattern):
                results.append(key)
    return sorted(results)
