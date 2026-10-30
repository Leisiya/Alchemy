import sys
import types
from datetime import date

import pandas as pd
import pytest

from sources import common
from sources.baostock_api import BaostockSource
from sources.common import Unsupported
from sources.sina import SinaSource


@pytest.mark.parametrize("symbol,ts_code", [
    ("600000", "600000.SH"), ("688981", "688981.SH"), ("000001", "000001.SZ"),
    ("300750", "300750.SZ"), ("430047", "430047.BJ"), ("920000", "920000.BJ"),
])
def test_ts_code_from_symbol(symbol, ts_code):
    assert common.ts_code_from_symbol(symbol) == ts_code
    assert common.from_prefixed(common.to_prefixed(ts_code)) == ts_code


def test_calendar_frame_is_newest_first_with_previous_trading_day():
    df = common.calendar_frame(["20261028", "20261029", "20261030", "20261102"], end_date="20261030", limit=2)

    assert df["cal_date"].tolist() == ["20261030", "20261029"]
    assert df["pretrade_date"].tolist() == ["20261029", "20261028"]
    assert set(df["is_open"]) == {"1"}


def test_with_price_changes_derives_from_previous_close():
    rows = common.with_price_changes([
        {"trade_date": "20261030", "close": 11.0},
        {"trade_date": "20261029", "close": 10.0},
    ])

    assert [r["pre_close"] for r in rows] == [None, 10.0]
    assert rows[1]["change"] == 1.0
    assert rows[1]["pct_chg"] == 10.0
    assert rows[0]["pct_chg"] is None


def test_recent_quarter_ends():
    assert common.recent_quarter_ends(date(2026, 10, 30), 3) == ["2026-09-30", "2026-06-30", "2026-03-31"]
    assert common.recent_quarter_ends(date(2026, 3, 31), 2) == ["2026-03-31", "2025-12-31"]


def test_sina_calendar_and_history_use_tushare_units(monkeypatch):
    fake = types.SimpleNamespace(
        tool_trade_date_hist_sina=lambda: pd.DataFrame({"trade_date": pd.to_datetime(["2026-10-29", "2026-10-30", "2026-11-02"])}),
        stock_zh_a_daily=lambda **kw: pd.DataFrame({
            "date": pd.to_datetime(["2026-10-29", "2026-10-30"]),
            "open": [9.85, 9.98], "high": [10.01, 10.04], "low": [9.84, 9.90], "close": [9.99, 10.02],
            "volume": [75394914.0, 64886491.0], "amount": [748543850.0, 647741483.0],
        }),
    )
    monkeypatch.setitem(sys.modules, "akshare", fake)
    source = SinaSource()

    cal = source.trade_cal(end_date="20261030", limit=5)
    df = source.daily(ts_code="600000.SH", start_date="20261029", end_date="20261030")

    assert cal["cal_date"].tolist() == ["20261030", "20261029"]
    assert df.iloc[1]["vol"] == pytest.approx(648864.91)  # shares -> lots
    assert df.iloc[1]["amount"] == pytest.approx(647741.483)  # CNY -> thousand CNY
    assert df.iloc[1]["pre_close"] == 9.99
    with pytest.raises(Unsupported):
        source.daily(trade_date="20261030")


class FakeResultSet:
    def __init__(self, fields, rows, error_code="0"):
        self.fields, self._rows, self.error_code, self.error_msg = fields, list(rows), error_code, "err"

    def next(self):
        return bool(self._rows)

    def get_row_data(self):
        return self._rows.pop(0)


def fake_baostock(**queries):
    module = types.SimpleNamespace(
        login=lambda: types.SimpleNamespace(error_code="0", error_msg=""),
        logout=lambda: None,
        **queries,
    )
    return module


def test_baostock_stock_basic_keeps_listed_stocks_and_cleans_industry(monkeypatch):
    monkeypatch.setitem(sys.modules, "baostock", fake_baostock(
        query_stock_industry=lambda: FakeResultSet(["code", "industry"], [["sh.600000", "J66货币金融服务"]]),
        query_stock_basic=lambda: FakeResultSet(
            ["code", "code_name", "ipoDate", "outDate", "type", "status"],
            [
                ["sh.600000", "浦发银行", "1999-11-10", "", "1", "1"],
                ["sh.000001", "上证综合指数", "1991-07-15", "", "2", "1"],
                ["sh.600001", "邯郸钢铁", "1998-01-22", "2009-12-29", "1", "0"],
            ],
        ),
    ))

    df = BaostockSource().stock_basic()

    assert df.to_dict("records") == [{
        "ts_code": "600000.SH", "symbol": "600000", "name": "浦发银行", "industry": "货币金融服务",
        "exchange": "SSE", "list_status": "L", "list_date": "19991110",
    }]


def test_baostock_history_skips_suspended_days_and_converts_units(monkeypatch):
    fields = ["date", "open", "high", "low", "close", "preclose", "volume", "amount", "pctChg", "tradestatus"]
    calls = {}

    def query(code, _fields, **kwargs):
        calls.update(code=code, **kwargs)
        return FakeResultSet(fields, [
            ["2026-10-29", "9.85", "10.01", "9.84", "9.99", "9.9", "75394914", "748543850", "0.9", "1"],
            ["2026-10-30", "9.99", "9.99", "9.99", "9.99", "9.99", "0", "0", "0", "0"],
        ])

    monkeypatch.setitem(sys.modules, "baostock", fake_baostock(query_history_k_data_plus=query))

    df = BaostockSource().daily(ts_code="600000.SH", start_date="20261029", end_date="20261030")

    assert calls["code"] == "sh.600000" and calls["adjustflag"] == "3"
    assert df["trade_date"].tolist() == ["20261029"]
    assert df.iloc[0]["vol"] == pytest.approx(753949.14)
    with pytest.raises(Unsupported):
        BaostockSource().daily(ts_code="920000.BJ", start_date="20261029", end_date="20261030")


def test_baostock_roe_is_converted_to_percent(monkeypatch):
    monkeypatch.setattr("sources.baostock_api.today_cn", lambda: "20261030")
    seen = []

    def query(code, year, quarter):
        seen.append((year, quarter))
        rows = [["sh.600000", "2026-08-28", "2026-06-30", "0.037501"]] if (year, quarter) == (2026, 2) else []
        return FakeResultSet(["code", "pubDate", "statDate", "roeAvg"], rows)

    monkeypatch.setitem(sys.modules, "baostock", fake_baostock(query_profit_data=query))

    df = BaostockSource().fina_indicator(ts_code="600000.SH")

    assert seen[:4] == [(2026, 3), (2026, 2), (2026, 1), (2025, 4)]
    assert df.to_dict("records") == [
        {"ts_code": "600000.SH", "ann_date": "20260828", "end_date": "20260630", "roe": 3.7501, "update_flag": "0"}
    ]


def test_baostock_query_errors_are_raised(monkeypatch):
    monkeypatch.setitem(sys.modules, "baostock", fake_baostock(
        query_trade_dates=lambda **_k: FakeResultSet(["calendar_date", "is_trading_day"], [], error_code="10002007"),
    ))

    with pytest.raises(RuntimeError, match="BaoStock"):
        BaostockSource().trade_cal(end_date="20261030", limit=1)
