from unittest.mock import MagicMock

import pandas as pd

from sync import daily_quote


def test_sync_skips_when_already_synced(monkeypatch):
    conn = MagicMock()
    pro = MagicMock()
    monkeypatch.setattr("sync.daily_quote.repo.has_synced", lambda *_a, **_k: True)
    result = daily_quote.sync(conn, pro, "20260601")
    assert result == 0
    pro.daily.assert_not_called()


def test_sync_fetches_and_upserts_when_not_synced(monkeypatch):
    conn = MagicMock()
    pro = MagicMock()
    df = pd.DataFrame({
        "ts_code": ["A.SH"], "trade_date": ["20260601"], "open": [1.0], "high": [1.1],
        "low": [0.9], "close": [1.05], "pre_close": [1.0], "change": [0.05],
        "pct_chg": [5.0], "vol": [100.0], "amount": [105.0],
    })
    pro.daily.return_value = df
    monkeypatch.setattr("sync.daily_quote.repo.has_synced", lambda *_a, **_k: False)
    upsert_calls = []
    monkeypatch.setattr("sync.daily_quote.repo.upsert_daily_quote", lambda _conn, rows: upsert_calls.append(rows) or len(rows))
    record_calls = []
    monkeypatch.setattr("sync.daily_quote.repo.record_sync", lambda *args: record_calls.append(args))

    result = daily_quote.sync(conn, pro, "20260601")

    assert result == 1
    assert upsert_calls[0][0]["ts_code"] == "A.SH"
    assert record_calls[0][4] == "0"  # status success
    conn.commit.assert_called_once()


def test_sync_records_failure_and_reraises_on_error(monkeypatch):
    conn = MagicMock()
    pro = MagicMock()
    pro.daily.side_effect = RuntimeError("boom")
    monkeypatch.setattr("sync.daily_quote.repo.has_synced", lambda *_a, **_k: False)
    record_calls = []
    monkeypatch.setattr("sync.daily_quote.repo.record_sync", lambda *args: record_calls.append(args))

    try:
        daily_quote.sync(conn, pro, "20260601")
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass

    assert record_calls[0][4] == "1"  # status failed
    conn.rollback.assert_called_once()
    conn.commit.assert_called_once()


def test_quote_sync_does_not_record_success_when_tushare_returns_empty(monkeypatch):
    conn = MagicMock()
    pro = MagicMock()
    pro.daily.return_value = pd.DataFrame()
    monkeypatch.setattr("sync.daily_quote.repo.has_synced", lambda *_a, **_k: False)
    record_calls = []
    monkeypatch.setattr("sync.daily_quote.repo.record_sync", lambda *args: record_calls.append(args))
    monkeypatch.setattr("sync.daily_quote.repo.upsert_daily_quote", lambda *_a, **_k: 0)

    result = daily_quote.sync(conn, pro, "20260827")

    assert result == 0
    assert record_calls == []
    conn.commit.assert_not_called()


def test_daily_basic_sync_does_not_record_success_when_tushare_returns_empty(monkeypatch):
    from sync import daily_basic

    conn = MagicMock()
    pro = MagicMock()
    pro.daily_basic.return_value = pd.DataFrame()
    monkeypatch.setattr("sync.daily_basic.repo.has_synced", lambda *_a, **_k: False)
    record_calls = []
    monkeypatch.setattr("sync.daily_basic.repo.record_sync", lambda *args: record_calls.append(args))
    monkeypatch.setattr("sync.daily_basic.repo.upsert_daily_basic", lambda *_a, **_k: 0)

    result = daily_basic.sync(conn, pro, "20260827")

    assert result == 0
    assert record_calls == []
    conn.commit.assert_not_called()
