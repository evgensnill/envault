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
    """Return reminder entries for keys that are due or overdue."""
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
