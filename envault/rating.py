"""Key quality rating: score each secret based on length, entropy, and age."""
from __future__ import annotations

import math
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envault.rotation import last_rotated


_MAX_SCORE = 100
_IDEAL_LENGTH = 32
_STALE_DAYS = 90


def _rating_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".ratings.json")


def _load(vault_path: str) -> dict:
    p = _rating_path(vault_path)
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save(vault_path: str, data: dict) -> None:
    _rating_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class RatingResult:
    key: str
    score: int          # 0-100
    grade: str          # A/B/C/D/F
    entropy_bits: float
    length_ok: bool
    freshness_ok: bool


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    freq = {c: value.count(c) / len(value) for c in set(value)}
    return -sum(p * math.log2(p) for p in freq.values())


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def rate_key(vault_path: str, key: str, value: str) -> RatingResult:
    """Compute a quality score for a single key/value pair."""
    import datetime

    score = 0

    # Length component (up to 40 pts)
    length_ok = len(value) >= _IDEAL_LENGTH
    score += min(40, int(40 * len(value) / _IDEAL_LENGTH))

    # Entropy component (up to 40 pts)
    ent = _entropy(value)
    ent_score = min(40, int(40 * ent / 5.0))  # 5 bits/char is excellent
    score += ent_score

    # Freshness component (up to 20 pts)
    ts = last_rotated(vault_path, key)
    freshness_ok = False
    if ts is not None:
        age_days = (datetime.datetime.utcnow() - ts).days
        freshness_ok = age_days <= _STALE_DAYS
        score += max(0, 20 - int(20 * age_days / _STALE_DAYS))

    score = min(_MAX_SCORE, score)
    return RatingResult(
        key=key,
        score=score,
        grade=_grade(score),
        entropy_bits=round(ent, 2),
        length_ok=length_ok,
        freshness_ok=freshness_ok,
    )


def rate_vault(vault_path: str, vault) -> list[RatingResult]:
    """Rate all keys in the vault."""
    results = []
    for key in vault.list_keys():
        try:
            value = vault.get(key)
        except Exception:
            continue
        results.append(rate_key(vault_path, key, value))
    return results


def save_rating(vault_path: str, result: RatingResult) -> None:
    data = _load(vault_path)
    data[result.key] = {
        "score": result.score,
        "grade": result.grade,
        "entropy_bits": result.entropy_bits,
        "length_ok": result.length_ok,
        "freshness_ok": result.freshness_ok,
    }
    _save(vault_path, data)


def get_saved_rating(vault_path: str, key: str) -> Optional[dict]:
    return _load(vault_path).get(key)
