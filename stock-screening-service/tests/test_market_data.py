import pandas as pd
import pytest
import requests

import sources.market_data as md
from sources.common import DataNotReady, Unsupported
from sources.market_data import AllSourcesFailed, MarketData


class Source:
    def __init__(self, name, **methods):
        self.name = name
        self.calls = []
        for method, behaviour in methods.items():
            setattr(self, method, self._wrap(method, behaviour))

    def _wrap(self, method, behaviour):
        def call(**kwargs):
            self.calls.append((method, kwargs))
            if isinstance(behaviour, Exception):
                raise behaviour
            return behaviour(**kwargs) if callable(behaviour) else behaviour
        return call


def calendar(days):
    return pd.DataFrame({"cal_date": list(reversed(days))})


def market_day(trade_date, count=md.MIN_MARKET_ROWS):
    return pd.DataFrame({
        "ts_code": [f"{i:06d}.SZ" for i in range(count)],
        "trade_date": [trade_date] * count,
        "close": [10.0] * count,
        "total_mv": [600000.0] * count,
    })


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(md.time, "sleep", lambda _s: None)


def test_falls_back_to_next_source_on_error_and_records_which_one_served():
    first = Source("a", trade_cal=RuntimeError("boom"))
    second = Source("b", trade_cal=calendar(["20261029", "20261030"]))
    data = MarketData([first, second])

    df = data.trade_cal(end_date="20261030", limit=2)

    assert sorted(df["cal_date"]) == ["20261029", "20261030"]
    assert data.used["trade_cal"] == "b"


def test_skips_sources_without_the_method_or_that_do_not_support_the_query():
    no_method = Source("none")
    unsupported = Source("u", daily=Unsupported("past date"))
    good = Source("g", daily=market_day("20260601"))
    data = MarketData([no_method, unsupported, good])

    assert len(data.daily(trade_date="20260601")) == md.MIN_MARKET_ROWS
    assert data.used["daily"] == "g"


def test_returns_empty_frame_when_data_is_not_published_yet():
    data = MarketData([
        Source("a", daily_basic=DataNotReady("before close")),
        Source("b", daily_basic=pd.DataFrame()),
        Source("c", daily_basic=RuntimeError("down")),
    ])

    assert data.daily_basic(trade_date="20261030").empty


def test_raises_with_every_source_error_when_all_fail():
    data = MarketData([Source("a", stock_basic=RuntimeError("boom")), Source("b", stock_basic=ValueError("bad"))])

    with pytest.raises(AllSourcesFailed) as info:
        data.stock_basic()

    assert "a: RuntimeError: boom" in str(info.value)
    assert "b: ValueError: bad" in str(info.value)


def test_rejects_data_that_fails_validation():
    stale = Source("stale", trade_cal=calendar(["20260101"]))
    partial = Source("partial", daily_basic=market_day("20261030", count=10))
    wrong_day = Source("wrong", daily_basic=market_day("20261029"))
    good = Source("good", trade_cal=calendar(["20261030"]), daily_basic=market_day("20261030"))
    data = MarketData([stale, partial, wrong_day, good])

    assert data.trade_cal(end_date="20261030", limit=1)["cal_date"].tolist() == ["20261030"]
    assert data.used["trade_cal"] == "good"
    assert len(data.daily_basic(trade_date="20261030")) == md.MIN_MARKET_ROWS
    assert data.used["daily_basic"] == "good"


def test_rejects_market_day_where_most_valuations_are_missing():
    df = market_day("20261030")
    df.loc[: len(df) // 2, "total_mv"] = None
    data = MarketData([Source("holes", daily_basic=df), Source("good", daily_basic=market_day("20261030"))])

    data.daily_basic(trade_date="20261030")

    assert data.used["daily_basic"] == "good"


def test_rejects_per_stock_history_for_another_stock_or_outside_the_range():
    other = pd.DataFrame({"ts_code": ["B.SZ"], "trade_date": ["20260601"], "close": [1.0]})
    outside = pd.DataFrame({"ts_code": ["A.SZ"], "trade_date": ["20250101"], "close": [1.0]})
    good = pd.DataFrame({"ts_code": ["A.SZ"], "trade_date": ["20260601"], "close": [1.0]})
    data = MarketData([Source("other", daily=other), Source("outside", daily=outside), Source("good", daily=good)])

    data.daily(ts_code="A.SZ", start_date="20260501", end_date="20260630")

    assert data.used["daily"] == "good"


def test_retries_transient_network_errors_before_falling_back():
    attempts = []

    def flaky(**_kwargs):
        attempts.append(1)
        if len(attempts) < 3:
            raise requests.ConnectionError("reset")
        return calendar(["20261030"])

    data = MarketData([Source("flaky", trade_cal=flaky)])

    assert not data.trade_cal(end_date="20261030", limit=1).empty
    assert len(attempts) == 3


def test_does_not_retry_permanent_errors():
    source = Source("a", trade_cal=ValueError("no permission"))
    data = MarketData([source, Source("b", trade_cal=calendar(["20261030"]))])

    data.trade_cal(end_date="20261030", limit=1)

    assert len(source.calls) == 1


def test_source_failing_repeatedly_is_skipped_for_the_rest_of_the_run():
    dead = Source("dead", fina_indicator=RuntimeError("down"))
    good = Source("good", fina_indicator=pd.DataFrame([{"ts_code": "A.SH", "roe": 1.0}]))
    data = MarketData([dead, good])

    for _ in range(md.CIRCUIT_BREAK_AFTER + 2):
        data.fina_indicator(ts_code="A.SH")

    assert len(dead.calls) == md.CIRCUIT_BREAK_AFTER


def test_close_closes_every_source_even_if_one_fails():
    closed = []

    class Closing:
        def __init__(self, name, fail=False):
            self.name, self.fail = name, fail

        def close(self):
            closed.append(self.name)
            if self.fail:
                raise RuntimeError("boom")

    MarketData([Closing("a", fail=True), Closing("b")]).close()

    assert closed == ["a", "b"]


def test_build_market_data_uses_free_sources_without_token(monkeypatch):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)

    names = [p.name for p in md.build_market_data().providers]

    assert names == ["tencent", "eastmoney", "sina", "baostock"]


def test_build_market_data_puts_tushare_first_with_token(monkeypatch):
    monkeypatch.setenv("TUSHARE_TOKEN", "abc")
    monkeypatch.setattr("clients.tushare_client.get_pro", lambda: object())

    names = [p.name for p in md.build_market_data().providers]

    assert names == ["tushare", "tencent", "eastmoney", "sina", "baostock"]
