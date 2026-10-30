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


def _stub_sync(monkeypatch, trade_dates, stock_basic=lambda *_a, **_k: 1):
    monkeypatch.setattr(sync_run, "ensure_trade_date", lambda *_a, **_k: trade_dates[-1])
    monkeypatch.setattr(sync_run, "stock_basic_sync", stock_basic)
    monkeypatch.setattr(sync_run, "trade_cal_sync", lambda *_a, **_k: 1)
    monkeypatch.setattr(sync_run, "daily_basic_sync", lambda *_a, **_k: 10)
    pro = MagicMock()
    pro.trade_cal.return_value = pd.DataFrame({"cal_date": list(reversed(trade_dates))})
    return pro


def test_run_sync_reuses_cached_stock_list_when_every_source_fails(monkeypatch):
    pro = _stub_sync(
        monkeypatch,
        ["20261030"],
        stock_basic=lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("all sources down")),
    )
    monkeypatch.setattr(sync_run, "fetch_stock_basic", lambda _conn: pd.DataFrame([{"ts_code": "A.SH"}]))
    monkeypatch.setattr(sync_run, "daily_quote_sync", lambda *_a, **_k: 1)

    out = sync_run.run_sync(MagicMock(), pro, "20261030")

    assert out["stock_basic"] == 0
    assert out["daily_quote"] == 1


def test_run_sync_fails_when_stock_list_cannot_be_fetched_or_reused(monkeypatch):
    pro = _stub_sync(
        monkeypatch,
        ["20261030"],
        stock_basic=lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("all sources down")),
    )
    monkeypatch.setattr(sync_run, "fetch_stock_basic", lambda _conn: pd.DataFrame())

    with pytest.raises(RuntimeError, match="all sources down"):
        sync_run.run_sync(MagicMock(), pro, "20261030")


def test_run_sync_backfills_candidates_when_whole_market_days_fail(monkeypatch):
    pro = _stub_sync(monkeypatch, ["20261028", "20261029", "20261030"])

    def quote_sync(_conn, _pro, day):
        if day == "20261029":
            raise RuntimeError("no source for this day")
        return 5

    monkeypatch.setattr(sync_run, "daily_quote_sync", quote_sync)
    monkeypatch.setattr(sync_run, "fetch_daily_basic", lambda *_a: pd.DataFrame([
        {"ts_code": "A.SH", "pe_ttm": 6.0, "dv_ttm": 5.0, "total_mv": 900000.0},
        {"ts_code": "B.SH", "pe_ttm": 6.0, "dv_ttm": 5.0, "total_mv": 900000.0},
        {"ts_code": "C.SH", "pe_ttm": 60.0, "dv_ttm": 0.5, "total_mv": 900000.0},
    ]))
    monkeypatch.setattr(sync_run, "fetch_stock_basic", lambda *_a: pd.DataFrame(
        [{"ts_code": code, "name": code, "industry": "银行"} for code in ("A.SH", "B.SH", "C.SH")]
    ))

    def daily(ts_code, start_date, end_date):
        if ts_code == "B.SH":
            raise RuntimeError("per-stock source down too")
        return pd.DataFrame([{"ts_code": ts_code, "trade_date": day, "close": 1.0} for day in ("20261029", "20261030")])

    pro.daily.side_effect = daily
    upserted = []
    monkeypatch.setattr(sync_run, "upsert_daily_quote", lambda _conn, rows: upserted.extend(rows) or len(rows))

    out = sync_run.run_sync(MagicMock(), pro, "20261030")

    assert out["daily_quote"] == 10
    assert out["failed_quote_dates"] == ["20261029"]
    assert out["quote_backfill"] == 2
    assert {c.kwargs["ts_code"] for c in pro.daily.call_args_list} == {"A.SH", "B.SH"}
    assert pro.daily.call_args_list[0].kwargs["start_date"] == "20261029"
    assert {row["ts_code"] for row in upserted} == {"A.SH"}
