import pandas as pd
import pytest

import sources.eastmoney as eastmoney
from sources.common import DataNotReady, Unsupported


class FakeResponse:
    def __init__(self, body):
        self._body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self._body


class FakeDataCenter:
    """Answers datacenter queries from in-memory tables, paging like the real API."""

    def __init__(self, tables):
        self.tables = tables
        self.calls = []

    def get(self, _url, params, **_kwargs):
        self.calls.append(params)
        rows = self.tables.get((params["reportName"], params.get("filter")))
        if params.get("sortTypes") == -1:
            rows = self.tables.get((params["reportName"], "latest"))
        if not rows:
            return FakeResponse({"success": False, "message": "返回数据为空", "result": None})
        size, page = int(params["pageSize"]), int(params["pageNumber"])
        pages = (len(rows) + size - 1) // size
        return FakeResponse({"success": True, "result": {"pages": pages, "data": rows[(page - 1) * size: page * size]}})


def valuation(code, close=10.0, pe_ttm=6.5, board="银行Ⅱ"):
    return {
        "SECUCODE": code, "SECURITY_CODE": code.split(".")[0], "SECURITY_NAME_ABBR": f"name{code}",
        "BOARD_NAME": board, "TRADE_DATE": "2026-10-30 00:00:00", "CLOSE_PRICE": close, "CHANGE_RATE": 0.3,
        "PE_TTM": pe_ttm, "PE_LAR": 6.7, "PB_MRQ": 0.44, "PS_TTM": 1.7, "TOTAL_MARKET_CAP": 333724499766,
        "NOTLIMITED_MARKETCAP_A": 333724499766, "TOTAL_SHARES": 33305838300, "FREE_SHARES_A": 33305838300,
    }


def bonus(code, per_ten, ex_date):
    return {"SECUCODE": code, "PRETAX_BONUS_RMB": per_ten, "EX_DIVIDEND_DATE": f"{ex_date} 00:00:00"}


VALUATION_FILTER = "(TRADE_DATE='2026-10-30')"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(eastmoney.time, "sleep", lambda _s: None)
    monkeypatch.setattr(eastmoney, "today_cn", lambda: "20261030")


def test_daily_basic_converts_units_and_computes_ttm_dividend_yield_by_ex_date():
    # real plans as of 2026-10-30
    tables = {
        ("RPT_VALUEANALYSIS_DET", VALUATION_FILTER): [
            valuation("601398.SH", close=8.75),
            valuation("600519.SH", close=1392.05),
            valuation("000002.SZ", close=5.0, pe_ttm=-3),
        ],
        ("RPT_SHAREBONUS_DET", "(REPORT_DATE='2026-06-30')"): [
            bonus("601398.SH", 1.511, "2026-10-21"),
            {"SECUCODE": "600519.SH", "PRETAX_BONUS_RMB": None, "EX_DIVIDEND_DATE": None},  # pre-announcement only
        ],
        ("RPT_SHAREBONUS_DET", "(REPORT_DATE='2025-12-31')"): [
            bonus("601398.SH", 1.689, "2026-05-13"),
            bonus("600519.SH", 280.2423, "2026-06-26"),
        ],
        ("RPT_SHAREBONUS_DET", "(REPORT_DATE='2025-09-30')"): [bonus("600519.SH", 239.57, "2025-12-19")],
        # ICBC moved its interim payout earlier, so three dividends were ex-dated within the year
        ("RPT_SHAREBONUS_DET", "(REPORT_DATE='2025-06-30')"): [bonus("601398.SH", 1.414, "2025-12-15")],
        ("RPT_SHAREBONUS_DET", "(REPORT_DATE='2024-12-31')"): [
            bonus("601398.SH", 1.646, "2025-07-14"),  # more than a year ago
            bonus("000002.SZ", 9.8, "2025-07-14"),  # nothing paid within the last year: no TTM yield
        ],
    }
    source = eastmoney.EastmoneySource(session=FakeDataCenter(tables))

    df = source.daily_basic(trade_date="20261030").set_index("ts_code")

    assert df.loc["601398.SH", "dv_ttm"] == pytest.approx(5.2731, abs=1e-4)
    assert df.loc["600519.SH", "dv_ttm"] == pytest.approx(3.7341, abs=1e-4)
    assert pd.isna(df.loc["000002.SZ", "dv_ttm"])
    assert df.loc["601398.SH", "total_mv"] == pytest.approx(33372449.9766)  # CNY -> 10k CNY
    assert df.loc["601398.SH", "total_share"] == pytest.approx(3330583.83)
    assert pd.isna(df.loc["000002.SZ", "pe_ttm"])


def test_dividend_announced_but_not_yet_ex_dividend_is_not_counted():
    tables = {
        ("RPT_VALUEANALYSIS_DET", VALUATION_FILTER): [valuation("600000.SH")],
        ("RPT_SHAREBONUS_DET", "(REPORT_DATE='2026-06-30')"): [bonus("600000.SH", 1.0, "2026-11-20")],
        ("RPT_SHAREBONUS_DET", "(REPORT_DATE='2025-12-31')"): [bonus("600000.SH", 4.2, "2026-07-16")],
    }

    df = eastmoney.EastmoneySource(session=FakeDataCenter(tables)).daily_basic(trade_date="20261030")

    assert df.loc[0, "dv_ttm"] == pytest.approx(4.2)


def test_dividends_paid_before_a_bonus_share_issue_are_per_current_share():
    def plan(cash, bonus_per_ten, ex_date):
        return {"SECUCODE": "000028.SZ", "PRETAX_BONUS_RMB": cash, "BONUS_IT_RATIO": bonus_per_ten,
                "EX_DIVIDEND_DATE": f"{ex_date} 00:00:00"}

    tables = {
        ("RPT_VALUEANALYSIS_DET", VALUATION_FILTER): [valuation("000028.SZ", close=10.0)],
        # 10送1派6.16 in one plan, then a 10转5 issue with no cash
        ("RPT_SHAREBONUS_DET", "(REPORT_DATE='2025-12-31')"): [plan(6.16, 1, "2026-06-24")],
        ("RPT_SHAREBONUS_DET", "(REPORT_DATE='2026-06-30')"): [plan(None, 5, "2026-09-01")],
    }

    df = eastmoney.EastmoneySource(session=FakeDataCenter(tables)).daily_basic(trade_date="20261030")

    assert df.loc[0, "dv_ttm"] == pytest.approx(0.616 / 1.1 / 1.5 / 10 * 100, abs=1e-4)


def test_daily_basic_without_dividends_leaves_yield_empty():
    tables = {("RPT_VALUEANALYSIS_DET", VALUATION_FILTER): [valuation("600000.SH")]}

    df = eastmoney.EastmoneySource(session=FakeDataCenter(tables)).daily_basic(trade_date="20261030")

    assert pd.isna(df.loc[0, "dv_ttm"])


def test_missing_trading_day_is_reported_as_not_ready():
    source = eastmoney.EastmoneySource(session=FakeDataCenter({}))

    with pytest.raises(DataNotReady):
        source.daily(trade_date="20261030")


def test_daily_by_date_pages_through_and_is_cached(monkeypatch):
    monkeypatch.setattr(eastmoney, "PAGE_SIZE", 2)
    rows = [valuation(f"{i:06d}.SZ") for i in range(5)]
    session = FakeDataCenter({("RPT_VALUEANALYSIS_DET", VALUATION_FILTER): rows})
    source = eastmoney.EastmoneySource(session=session)

    first = source.daily(trade_date="20261030")
    source.daily(trade_date="20261030")

    assert len(first) == 5
    assert len(session.calls) == 3
    assert first.loc[0, "close"] == 10.0


def test_daily_by_stock_is_unsupported():
    with pytest.raises(Unsupported):
        eastmoney.EastmoneySource(session=FakeDataCenter({})).daily(ts_code="600000.SH")


def test_stock_basic_uses_latest_trading_day_and_strips_board_level():
    tables = {
        ("RPT_VALUEANALYSIS_DET", "latest"): [{"TRADE_DATE": "2026-10-30 00:00:00"}],
        ("RPT_VALUEANALYSIS_DET", VALUATION_FILTER): [valuation("600000.SH"), valuation("920000.BJ", board="")],
    }

    df = eastmoney.EastmoneySource(session=FakeDataCenter(tables)).stock_basic().set_index("ts_code")

    assert df.loc["600000.SH", "industry"] == "银行"
    assert df.loc["600000.SH", "exchange"] == "SSE"
    assert pd.isna(df.loc["920000.BJ", "industry"])
    assert df.loc["920000.BJ", "exchange"] == "BSE"


def test_fina_indicator_keeps_latest_announcement_per_period():
    def report(code, period, notice, roe):
        return {"SECUCODE": code, "REPORTDATE": f"{period} 00:00:00", "NOTICE_DATE": f"{notice} 00:00:00", "WEIGHTAVG_ROE": roe}

    tables = {
        ("RPT_LICO_FN_CPD", "(REPORTDATE='2026-09-30')"): [report("600000.SH", "2026-09-30", "2026-10-28", 5.1)],
        ("RPT_LICO_FN_CPD", "(REPORTDATE='2026-06-30')"): [
            report("600000.SH", "2026-06-30", "2026-08-28", 3.9),
            report("600000.SH", "2026-06-30", "2026-09-15", 3.96),
        ],
    }
    session = FakeDataCenter(tables)
    source = eastmoney.EastmoneySource(session=session)

    df = source.fina_indicator(ts_code="600000.SH").sort_values("end_date")
    source.fina_indicator(ts_code="000001.SZ")

    assert df[["end_date", "ann_date", "roe"]].values.tolist() == [
        ["20260630", "20260915", 3.96],
        ["20260930", "20261028", 5.1],
    ]
    assert len(session.calls) == 3  # three report periods, loaded once for all stocks


def test_real_api_errors_are_raised():
    class Broken:
        def get(self, *_a, **_k):
            return FakeResponse({"success": False, "message": "参数错误"})

    with pytest.raises(RuntimeError, match="参数错误"):
        eastmoney.EastmoneySource(session=Broken()).daily(trade_date="20261030")
