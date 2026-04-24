"""Rotation reminder / due-date tracking for vault keys."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, NamedTuple, Optional

from envault.rotation import last_rotated
from envault.vault import Vault


class ReminderEntry(NamedTuple):
    key: str
    last_rotated: Optional[datetime]
    days_since: Optional[int]
    due_in: int  # negative means overdue
    overdue: bool


def check_reminders(
    vault: Vault,
    max_age_days: int = 90,
    keys: Optional[List[str]] = None,
) -> List[ReminderEntry]:
    """Return reminder entries for keys that are due or overdue.

    Args:
        vault: The vault instance to inspect.
        max_age_days: Number of days after which a key is considered overdue.
        keys: Specific keys to check; defaults to all keys in the vault.

    Returns:
        A list of :class:`ReminderEntry` objects, one per key checked.
    """
    target_keys = keys if keys is not None else vault.list_keys()
    entries: List[ReminderEntry] = []
    now = datetime.utcnow()

    for key in target_keys:
        ts = last_rotated(vault, key)
        if ts is None:
            entry = ReminderEntry(
                key=key,
                last_rotated=None,
                days_since=None,
                due_in=-max_age_days,
                overdue=True,
            )
        else:
            delta = now - ts
            days_since = delta.days
            due_in = max_age_days - days_since
            entry = ReminderEntry(
                key=key,
                last_rotated=ts,
                days_since=days_since,
                due_in=due_in,
                overdue=due_in < 0,
            )
        entries.append(entry)

    return entries


def overdue_keys(vault: Vault, max_age_days: int = 90) -> List[str]:
    """Return list of key names that are overdue for rotation."""
    return [e.key for e in check_reminders(vault, max_age_days) if e.overdue]


def upcoming_keys(vault: Vault, max_age_days: int = 90, within_days: int = 14) -> List[str]:
    """Return list of key names due for rotation within *within_days* days.

    Keys that are already overdue are excluded; use :func:`overdue_keys` for those.

    Args:
        vault: The vault instance to inspect.
        max_age_days: Number of days after which a key is considered overdue.
        within_days: Window in days to look ahead for upcoming rotations.

    Returns:
        Key names whose rotation is due within the specified window.
    """
    return [
        e.key
        for e in check_reminders(vault, max_age_days)
        if not e.overdue and e.due_in <= within_days
    ]
