"""Tests for envault.quota."""
import pytest

from envault.quota import (
    QuotaExceededError,
    QuotaInfo,
    check_quota,
    enforce_quota,
    get_quota,
    remove_quota,
    set_quota,
)


class _FakeVault:
    def __init__(self, keys):
        self._keys = keys

    def list_keys(self):
        return list(self._keys)


def _vp(tmp_path):
    return str(tmp_path / "vault.env")


def test_set_and_get_quota(tmp_path):
    vp = _vp(tmp_path)
    set_quota(vp, 10)
    assert get_quota(vp) == 10


def test_get_quota_returns_none_when_not_set(tmp_path):
    vp = _vp(tmp_path)
    assert get_quota(vp) is None


def test_set_quota_invalid_limit_raises(tmp_path):
    vp = _vp(tmp_path)
    with pytest.raises(ValueError, match="at least 1"):
        set_quota(vp, 0)


def test_remove_quota_returns_true(tmp_path):
    vp = _vp(tmp_path)
    set_quota(vp, 5)
    assert remove_quota(vp) is True
    assert get_quota(vp) is None


def test_remove_quota_no_quota_returns_false(tmp_path):
    vp = _vp(tmp_path)
    assert remove_quota(vp) is False


def test_quota_info_remaining(tmp_path):
    info = QuotaInfo(limit=10, current=3)
    assert info.remaining == 7
    assert info.exceeded is False


def test_quota_info_exceeded(tmp_path):
    info = QuotaInfo(limit=5, current=7)
    assert info.exceeded is True
    assert info.remaining == 0


def test_check_quota_within_limit(tmp_path):
    vp = _vp(tmp_path)
    set_quota(vp, 5)
    vault = _FakeVault(["A", "B", "C"])
    info = check_quota(vp, vault)
    assert info.current == 3
    assert info.limit == 5
    assert info.remaining == 2


def test_check_quota_exceeded_raises(tmp_path):
    vp = _vp(tmp_path)
    set_quota(vp, 2)
    vault = _FakeVault(["A", "B", "C"])
    with pytest.raises(QuotaExceededError, match="exceeds quota"):
        check_quota(vp, vault)


def test_check_quota_no_limit_raises_value_error(tmp_path):
    vp = _vp(tmp_path)
    vault = _FakeVault(["A"])
    with pytest.raises(ValueError, match="No quota configured"):
        check_quota(vp, vault)


def test_enforce_quota_allows_when_under_limit(tmp_path):
    vp = _vp(tmp_path)
    set_quota(vp, 5)
    vault = _FakeVault(["A", "B"])
    enforce_quota(vp, vault)  # should not raise


def test_enforce_quota_raises_at_limit(tmp_path):
    vp = _vp(tmp_path)
    set_quota(vp, 3)
    vault = _FakeVault(["A", "B", "C"])
    with pytest.raises(QuotaExceededError, match="quota reached"):
        enforce_quota(vp, vault)


def test_enforce_quota_no_limit_is_noop(tmp_path):
    vp = _vp(tmp_path)
    vault = _FakeVault(["A"] * 1000)
    enforce_quota(vp, vault)  # no quota set — should not raise
