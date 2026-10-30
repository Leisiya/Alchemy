from datetime import datetime

import pandas as pd
import pytest

import sources.tencent as tencent
from sources.common import CN_TZ, DataNotReady, Unsupported


def qt_record(prefixed, stamp="20261030161441", vol="648865", pe_ttm="6.51", **overrides):
    fields = [""] * 70
    values = {
        1: "浦发银行", 2: prefixed[2:], 3: "10.02", 4: "9.99", 5: "9.98", 6: vol, 30: stamp, 31: "0.03",
        32: "0.30", 33: "10.04", 34: "9.90", 36: vol, 37: "64774", 38: "0.19", 39: pe_ttm, 44: "3337.24",
        45: "3337.24", 46: "0.44", 49: "0.86", 53: "6.67", 64: "4.19",
    }
    values.update(overrides)
    for index, value in values.items():
        fields[index] = value
    return f'v_{prefixed}="' + "~".join(fields) + '";'


class FakeResponse:
    def __init__(self, text="", payload=None):
        self.text, self._payload, self.encoding = text, payload, None

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses, self.calls = list(responses), []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.pop(0)


def test_parse_snapshot_maps_fields_and_units():
    basic, quotes = tencent.parse_snapshot(qt_record("sh600000"), "20261030")

    assert basic == [{
        "ts_code": "600000.SH", "trade_date": "20261030", "close": 10.02, "turnover_rate": 0.19,
        "volume_ratio": 0.86, "pe": 6.67, "pe_ttm": 6.51, "pb": 0.44, "dv_ttm": 4.19,
        "total_mv": 33372400.0, "circ_mv": 33372400.0,
    }]
    assert quotes[0]["vol"] == 648865.0  # lots, like Tushare
    assert quotes[0]["amount"] == 647740.0  # 10k CNY -> thousand CNY
    assert quotes[0]["pre_close"] == 9.99


def test_parse_snapshot_drops_suspended_stale_and_short_records():
    text = "".join([
        qt_record("sz000001", vol="0"),
        qt_record("sh600001", stamp="20261029150000"),
        'v_sh600002="1~short~600002";',
        'v_pv_none_match="1";',
        qt_record("bj920000"),
    ])

    basic, quotes = tencent.parse_snapshot(text, "20261030")

    assert [row["ts_code"] for row in basic] == ["920000.BJ"]
    assert len(quotes) == 1


def test_parse_snapshot_leaves_loss_making_pe_empty():
    basic, _ = tencent.parse_snapshot(qt_record("sh600000", pe_ttm="-12.5"), "20261030")

    assert basic[0]["pe_ttm"] is None


def at(monkeypatch, hour, minute, day="20261030"):
    moment = datetime.strptime(day, "%Y%m%d").replace(hour=hour, minute=minute, tzinfo=CN_TZ)
    monkeypatch.setattr(tencent, "now_cn", lambda: moment)
    monkeypatch.setattr(tencent, "today_cn", lambda: day)
    monkeypatch.setattr(tencent.time, "sleep", lambda _s: None)


def test_snapshot_is_not_taken_before_the_close(monkeypatch):
    at(monkeypatch, 14, 59)
    source = tencent.TencentSource(universe=lambda: ["600000.SH"], session=FakeSession([]))

    with pytest.raises(DataNotReady):
        source.daily_basic(trade_date="20261030")


def test_snapshot_only_serves_today(monkeypatch):
    at(monkeypatch, 17, 0)
    source = tencent.TencentSource(universe=lambda: ["600000.SH"], session=FakeSession([]))

    with pytest.raises(Unsupported):
        source.daily(trade_date="20261029")


def test_snapshot_batches_codes_and_serves_basic_and_quotes_from_one_fetch(monkeypatch):
    at(monkeypatch, 17, 0)
    monkeypatch.setattr(tencent, "BATCH_SIZE", 2)
    session = FakeSession([
        FakeResponse(qt_record("sh600000") + qt_record("sz000001")),
        FakeResponse(qt_record("bj920000")),
    ])
    source = tencent.TencentSource(universe=lambda: ["600000.SH", "000001.SZ", "920000.BJ"], session=session)

    basic = source.daily_basic(trade_date="20261030")
    quotes = source.daily(trade_date="20261030")

    assert len(session.calls) == 2
    assert session.calls[0][0].endswith("q=sh600000,sz000001")
    assert len(basic) == len(quotes) == 3


def test_snapshot_needs_a_stock_list(monkeypatch):
    at(monkeypatch, 17, 0)
    source = tencent.TencentSource(universe=lambda: [], session=FakeSession([]))

    with pytest.raises(RuntimeError, match="股票列表"):
        source.daily_basic(trade_date="20261030")


def test_history_requests_unadjusted_range_and_derives_changes():
    payload = {"code": 0, "data": {"sh600000": {"day": [
        ["2026-10-29", "9.85", "9.99", "10.01", "9.84", "753949"],
        ["2026-10-30", "9.98", "10.02", "10.04", "9.90", "648865"],
    ]}}}
    session = FakeSession([FakeResponse(payload=payload)])

    df = tencent.TencentSource(session=session).daily(ts_code="600000.SH", start_date="20261029", end_date="20261030")

    assert session.calls[0][1]["params"]["param"] == "sh600000,day,2026-10-29,2026-10-30,640,"
    assert df["trade_date"].tolist() == ["20261029", "20261030"]
    last = df.iloc[-1]
    assert (last["open"], last["close"], last["pre_close"]) == (9.98, 10.02, 9.99)
    assert last["pct_chg"] == pytest.approx(0.3003, abs=1e-4)
    assert pd.isna(df.iloc[0]["pre_close"])


def test_history_raises_on_error_payload():
    session = FakeSession([FakeResponse(payload={"code": -1, "msg": "bad param"})])

    with pytest.raises(RuntimeError, match="bad param"):
        tencent.TencentSource(session=session).daily(ts_code="600000.SH", start_date="20261029", end_date="20261030")
