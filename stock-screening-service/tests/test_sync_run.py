from unittest.mock import MagicMock

import pandas as pd
import pytest

import pipeline.sync_run as sync_run


def test_run_sync_raises_when_same_day_daily_basic_empty_without_fallback(monkeypatch):
    conn = MagicMock()
    pro = MagicMock()
    pro.trade_cal.return_value = pd.DataFrame({"cal_date": ["20260825", "20260826", "20260827"]})

    monkeypatch.setattr(sync_run, "ensure_trade_date", lambda *_a, **_k: "20260827")
    monkeypatch.setattr(sync_run, "stock_basic_sync", lambda *_a, **_k: 1)
    monkeypatch.setattr(sync_run, "trade_cal_sync", lambda *_a, **_k: 1)
    monkeypatch.setattr(
        sync_run,
        "daily_basic_sync",
        lambda _conn, _pro, day: 0 if day == "20260827" else 10,
    )
    monkeypatch.setattr(
        sync_run,
        "fetch_daily_basic",
        lambda _conn, day: pd.DataFrame([{"ts_code": "A.SH"}]) if day == "20260826" else pd.DataFrame(),
    )
    quote_days = []
    monkeypatch.setattr(
        sync_run,
        "daily_quote_sync",
        lambda _conn, _pro, day: quote_days.append(day) or 1,
    )

    with pytest.raises(ValueError, match="估值"):
        sync_run.run_sync(conn, pro, "20260827")

    assert "20260826" not in quote_days


def test_run_sync_raises_when_no_daily_basic_after_fallback(monkeypatch):
    conn = MagicMock()
    pro = MagicMock()
    pro.trade_cal.return_value = pd.DataFrame({"cal_date": ["20260826", "20260827"]})

    monkeypatch.setattr(sync_run, "ensure_trade_date", lambda *_a, **_k: "20260827")
    monkeypatch.setattr(sync_run, "stock_basic_sync", lambda *_a, **_k: 1)
    monkeypatch.setattr(sync_run, "trade_cal_sync", lambda *_a, **_k: 1)
    monkeypatch.setattr(sync_run, "daily_basic_sync", lambda *_a, **_k: 0)
    monkeypatch.setattr(sync_run, "fetch_daily_basic", lambda *_a, **_k: pd.DataFrame())
    monkeypatch.setattr(sync_run, "daily_quote_sync", lambda *_a, **_k: 1)

    with pytest.raises(ValueError, match="估值"):
        sync_run.run_sync(conn, pro, "20260827")
