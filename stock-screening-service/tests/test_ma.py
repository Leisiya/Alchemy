import pandas as pd
import pytest

from indicators.ma import compute_ma, classify_signal


def test_compute_ma_returns_none_before_window_filled():
    history = pd.DataFrame({
        "ts_code": ["600000.SH"] * 5,
        "trade_date": ["20260101", "20260102", "20260103", "20260104", "20260105"],
        "close": [10.0, 10.0, 10.0, 10.0, 10.0],
    })
    result = compute_ma(history, window=120)
    assert result["ma120"].isna().all()


def test_compute_ma_computes_rolling_mean_once_window_filled():
    closes = [float(i) for i in range(1, 121)]  # 1..120
    history = pd.DataFrame({
        "ts_code": ["600000.SH"] * 120,
        "trade_date": [f"2026{str(i).zfill(4)}" for i in range(1, 121)],
        "close": closes,
    })
    result = compute_ma(history, window=120)
    expected_ma = sum(closes) / 120
    assert result["ma120"].iloc[-1] == pytest.approx(expected_ma)


def test_compute_ma_groups_by_ts_code_independently():
    history = pd.DataFrame({
        "ts_code": ["A"] * 120 + ["B"] * 120,
        "trade_date": [str(i) for i in range(240)],
        "close": [1.0] * 120 + [2.0] * 120,
    })
    result = compute_ma(history, window=120)
    a_last = result[result["ts_code"] == "A"]["ma120"].iloc[-1]
    b_last = result[result["ts_code"] == "B"]["ma120"].iloc[-1]
    assert a_last == pytest.approx(1.0)
    assert b_last == pytest.approx(2.0)


@pytest.mark.parametrize("ratio,expected", [
    (0.87, "破位低估"),
    (0.8799, "破位低估"),
    (0.88, None),
    (1.0, None),
    (1.12, None),
    (1.1201, "强势突破"),
    (1.5, "强势突破"),
])
def test_classify_signal_boundaries(ratio, expected):
    assert classify_signal(ratio) == expected
