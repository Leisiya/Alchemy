from unittest.mock import MagicMock

import pytest

from clients.tushare_client import call_with_retry, is_rate_limit_error


@pytest.mark.parametrize("message,expected", [
    ("HTTPError: 429 Too Many Requests", True),
    ("请求过于频繁，请稍后重试", True),
    ("connection reset", False),
    ("ValueError: bad token", False),
])
def test_is_rate_limit_error(message, expected):
    assert is_rate_limit_error(Exception(message)) is expected


def test_call_with_retry_retries_on_rate_limit_then_succeeds(monkeypatch):
    monkeypatch.setattr("clients.tushare_client.time.sleep", lambda _seconds: None)
    func = MagicMock(side_effect=[Exception("429 too many requests"), "ok"])
    result = call_with_retry(func, "a", key="b")
    assert result == "ok"
    assert func.call_count == 2
    func.assert_any_call("a", key="b")


def test_call_with_retry_raises_immediately_on_non_rate_limit_error():
    func = MagicMock(side_effect=ValueError("boom"))
    with pytest.raises(ValueError, match="boom"):
        call_with_retry(func)
    assert func.call_count == 1


def test_call_with_retry_raises_after_exhausting_attempts(monkeypatch):
    monkeypatch.setattr("clients.tushare_client.time.sleep", lambda _seconds: None)
    monkeypatch.setattr("clients.tushare_client.REQUEST_RETRY_TIMES", 2)
    func = MagicMock(side_effect=Exception("429 too many requests"))
    with pytest.raises(Exception, match="429"):
        call_with_retry(func)
    assert func.call_count == 2
