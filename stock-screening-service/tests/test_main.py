from unittest.mock import MagicMock

import pandas as pd
from fastapi.testclient import TestClient

import main
import pipeline.sync_run as sync_run
import pipeline.screen_run as screen_run


def test_health_reports_tushare_data_source():
    client = TestClient(main.app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["strategy_code"] == "HIGH_DIVIDEND_MA120"
    assert body["data_source"] == "tushare"


def test_sync_run_calls_all_datasets_in_order(monkeypatch):
    calls = []
    conn = MagicMock()
    pro = MagicMock()
    pro.trade_cal.return_value = pd.DataFrame({"cal_date": ["20260601"]})

    monkeypatch.setattr(main, "get_connection", lambda: conn)
    monkeypatch.setattr(main, "get_pro", lambda: pro)

    def make_sync(name):
        def _sync(*_a, **_k):
            calls.append(name)
            return 1

        return _sync

    for name in ("stock_basic_sync", "trade_cal_sync", "daily_basic_sync", "daily_quote_sync"):
        monkeypatch.setattr(sync_run, name, make_sync(name))

    client = TestClient(main.app)
    response = client.post(
        "/internal/sync/run",
        json={"trade_date": "20260601", "lookback_days": 1},
    )

    assert response.status_code == 200
    assert calls == [
        "stock_basic_sync",
        "trade_cal_sync",
        "daily_basic_sync",
        "daily_quote_sync",
    ]
    body = response.json()
    assert body["trade_date"] == "20260601"
    assert body["stock_basic"] == 1
    assert body["trade_cal"] == 1
    assert body["daily_basic"] == 1
    assert body["daily_quote"] == 1


def test_screening_run_reads_from_repositories(monkeypatch):
    monkeypatch.setattr(main, "get_connection", lambda: MagicMock())
    monkeypatch.setattr(main, "get_pro", lambda: MagicMock())
    monkeypatch.setattr(screen_run, "fetch_daily_basic", lambda _conn, _d: pd.DataFrame({
        "ts_code": ["A.SH"], "trade_date": ["20260601"], "pe_ttm": [10.0],
        "dv_ttm": [4.0], "total_mv": [600000.0], "pb": [1.0],
    }))
    monkeypatch.setattr(screen_run, "fetch_stock_basic", lambda _conn: pd.DataFrame({
        "ts_code": ["A.SH"], "name": ["Alpha"], "industry": ["银行"],
    }))
    history = pd.DataFrame({
        "ts_code": ["A.SH"] * 120,
        "trade_date": [f"2025{str(i).zfill(4)}" for i in range(1, 120)] + ["20260601"],
        "close": [100.0] * 119 + [80.0],
    })
    monkeypatch.setattr(screen_run, "fetch_daily_quotes", lambda *_a, **_k: history)

    client = TestClient(main.app)
    response = client.post(
        "/internal/screenings/high-dividend-ma120/run",
        json={"trade_date": "20260601"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["strategy_code"] == "HIGH_DIVIDEND_MA120"
    assert body["summary"]["total_count"] == 1
    assert body["results"][0]["ma120_signal"] == "破位低估"
