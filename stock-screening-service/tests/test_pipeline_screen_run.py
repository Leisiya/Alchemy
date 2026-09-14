from unittest.mock import MagicMock

import pandas as pd

import pipeline.screen_run as screen_run


def test_run_screen_returns_summary_and_results(monkeypatch):
    conn = MagicMock()
    pro = MagicMock()
    monkeypatch.setattr(screen_run, "ensure_trade_date", lambda value, _pro: "20260722")
    monkeypatch.setattr(
        screen_run,
        "fetch_daily_basic",
        lambda *_: pd.DataFrame(
            [{
                "ts_code": "601288.SH",
                "trade_date": "20260722",
                "pe_ttm": 5,
                "dv_ttm": 5,
                "pb": 1,
                "total_mv": 600000,
                "close": 4.0,
            }]
        ),
    )
    monkeypatch.setattr(
        screen_run,
        "fetch_stock_basic",
        lambda *_: pd.DataFrame([{"ts_code": "601288.SH", "name": "农业银行", "industry": "银行"}]),
    )
    monkeypatch.setattr(screen_run, "fetch_daily_quotes", lambda *_: pd.DataFrame())
    monkeypatch.setattr(
        screen_run,
        "apply_ma120_signal",
        lambda candidates, history, trade_date: candidates.assign(
            close_price=4.0, ma120=4.5, price_ma120_ratio=0.89, ma120_signal="破位低估"
        ),
    )
    monkeypatch.setattr(
        screen_run,
        "attach_candidate_roe",
        lambda *_: {"601288.SH": None},
    )
    out = screen_run.run_screen(conn, pro, "20260722")
    assert out["trade_date"] == "20260722"
    assert out["summary"]["total_count"] == 1
    assert out["results"][0]["ts_code"] == "601288.SH"
    assert out["results"][0]["dv_ttm"] == 5
    assert "roe" in out["results"][0]
    assert out["results"][0]["roe"] is None


def test_run_screen_counts_mid_band_in_total_not_in_signals(monkeypatch):
    conn = MagicMock()
    pro = MagicMock()
    monkeypatch.setattr(screen_run, "ensure_trade_date", lambda value, _pro: "20260722")
    monkeypatch.setattr(
        screen_run,
        "fetch_daily_basic",
        lambda *_: pd.DataFrame([
            {"ts_code": "LOW.SH", "trade_date": "20260722", "pe_ttm": 10, "dv_ttm": 4, "pb": 1, "total_mv": 600000, "close": 10.0},
            {"ts_code": "MID.SH", "trade_date": "20260722", "pe_ttm": 10, "dv_ttm": 5, "pb": 1, "total_mv": 800000, "close": 10.0},
            {"ts_code": "HIGH.SH", "trade_date": "20260722", "pe_ttm": 10, "dv_ttm": 6, "pb": 1, "total_mv": 900000, "close": 10.0},
        ]),
    )
    monkeypatch.setattr(
        screen_run,
        "fetch_stock_basic",
        lambda *_: pd.DataFrame([
            {"ts_code": "LOW.SH", "name": "L", "industry": "银行"},
            {"ts_code": "MID.SH", "name": "M", "industry": "银行"},
            {"ts_code": "HIGH.SH", "name": "H", "industry": "银行"},
        ]),
    )
    monkeypatch.setattr(screen_run, "fetch_daily_quotes", lambda *_: pd.DataFrame({"ts_code": ["x"]}))
    def assign_ma120(candidates, history, trade_date):
        ratio_by_code = {"LOW.SH": 0.8, "MID.SH": 1.0, "HIGH.SH": 1.3}
        signal_by_code = {"LOW.SH": "破位低估", "MID.SH": "", "HIGH.SH": "强势突破"}
        return candidates.assign(
            close_price=10.0,
            ma120=10.0,
            price_ma120_ratio=candidates["ts_code"].map(ratio_by_code),
            ma120_signal=candidates["ts_code"].map(signal_by_code),
        )

    monkeypatch.setattr(screen_run, "apply_ma120_signal", assign_ma120)
    monkeypatch.setattr(
        screen_run,
        "attach_candidate_roe",
        lambda *_a, **_k: {"LOW.SH": 8.0, "MID.SH": None, "HIGH.SH": 12.0},
    )
    out = screen_run.run_screen(conn, pro, "20260722")
    assert out["summary"]["total_count"] == 3
    assert out["summary"]["low_count"] == 1
    assert out["summary"]["high_count"] == 1
    mid = next(item for item in out["results"] if item["ts_code"] == "MID.SH")
    assert mid["ma120_signal"] == ""
    assert "roe" in mid
    assert mid["roe"] is None
    low = next(item for item in out["results"] if item["ts_code"] == "LOW.SH")
    assert low["roe"] == 8.0


def test_run_screen_does_not_call_attach_candidate_dividend(monkeypatch):
    conn = MagicMock()
    pro = MagicMock()
    monkeypatch.setattr(screen_run, "ensure_trade_date", lambda value, _pro: "20260722")
    monkeypatch.setattr(
        screen_run,
        "fetch_daily_basic",
        lambda *_: pd.DataFrame(
            [{
                "ts_code": "601288.SH",
                "trade_date": "20260722",
                "pe_ttm": 5,
                "dv_ttm": 5,
                "pb": 1,
                "total_mv": 600000,
                "close": 4.0,
            }]
        ),
    )
    monkeypatch.setattr(
        screen_run,
        "fetch_stock_basic",
        lambda *_: pd.DataFrame([{"ts_code": "601288.SH", "name": "农业银行", "industry": "银行"}]),
    )
    monkeypatch.setattr(screen_run, "fetch_daily_quotes", lambda *_: pd.DataFrame())
    monkeypatch.setattr(
        screen_run,
        "apply_ma120_signal",
        lambda candidates, history, trade_date: candidates.assign(
            close_price=4.0, ma120=4.5, price_ma120_ratio=0.89, ma120_signal="破位低估"
        ),
    )
    monkeypatch.setattr(
        screen_run,
        "attach_candidate_roe",
        lambda *_: {"601288.SH": None},
    )
    screen_run.run_screen(conn, pro, "20260722")
    assert not hasattr(screen_run, "attach_candidate_dividend")


def test_run_screen_normalizes_nan_signal_to_empty(monkeypatch):
    conn = MagicMock()
    pro = MagicMock()
    monkeypatch.setattr(screen_run, "ensure_trade_date", lambda value, _pro: "20260722")
    monkeypatch.setattr(
        screen_run,
        "fetch_daily_basic",
        lambda *_: pd.DataFrame([{
            "ts_code": "A.SH",
            "trade_date": "20260722",
            "pe_ttm": 10,
            "pb": 1,
            "dv_ttm": 4,
            "total_mv": 600000,
            "close": 10.0,
        }]),
    )
    monkeypatch.setattr(
        screen_run,
        "fetch_stock_basic",
        lambda *_: pd.DataFrame([{"ts_code": "A.SH", "name": "A", "industry": "银行"}]),
    )
    monkeypatch.setattr(screen_run, "fetch_daily_quotes", lambda *_: pd.DataFrame())
    monkeypatch.setattr(
        screen_run,
        "apply_ma120_signal",
        lambda candidates, history, trade_date: candidates.assign(
            close_price=pd.NA, ma120=pd.NA, price_ma120_ratio=pd.NA, ma120_signal=pd.NA
        ),
    )
    monkeypatch.setattr(screen_run, "attach_candidate_roe", lambda *_: {"A.SH": None})
    out = screen_run.run_screen(conn, pro, "20260722")
    assert out["results"][0]["ma120_signal"] == ""
    assert "roe" in out["results"][0]
    assert out["summary"]["total_count"] == 1
    assert out["summary"]["low_count"] == 0
    assert out["summary"]["high_count"] == 0
