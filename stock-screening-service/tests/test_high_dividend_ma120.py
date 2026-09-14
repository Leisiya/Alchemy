import pandas as pd

from strategies.high_dividend_ma120 import filter_by_fundamentals, apply_ma120_signal


def make_daily_basic():
    return pd.DataFrame({
        "ts_code": ["A.SH", "B.SH", "C.SH", "D.SH"],
        "trade_date": ["20260101"] * 4,
        "pe_ttm": [10.0, 25.0, 15.0, -1.0],   # B超过20被过滤；D为负被过滤
        "dv_ttm": [4.0, 4.0, 2.0, 5.0],        # Tushare 原值，筛股忽略
        "total_mv": [600_000.0, 600_000.0, 600_000.0, 600_000.0],
        "pb": [1.1, 1.2, 1.3, 1.4],
        "close": [10.0, 10.0, 10.0, 10.0],
    })


def make_stock_basic():
    return pd.DataFrame({
        "ts_code": ["A.SH", "B.SH", "C.SH", "D.SH"],
        "name": ["Alpha", "Beta", "Gamma", "Delta"],
        "industry": ["银行", "银行", "银行", "银行"],
    })


def test_filter_by_fundamentals_keeps_only_qualifying_rows():
    result = filter_by_fundamentals(make_daily_basic(), make_stock_basic())
    assert result["ts_code"].tolist() == ["A.SH"]
    assert result.iloc[0]["total_mv_yi"] == 60.0
    assert result.iloc[0]["dv_ttm"] == 4.0


def test_filter_by_fundamentals_does_not_admit_when_tushare_below_threshold():
    daily_basic = make_daily_basic()
    daily_basic.loc[daily_basic["ts_code"] == "A.SH", "dv_ttm"] = 2.0
    result = filter_by_fundamentals(daily_basic, make_stock_basic())
    assert result.empty


def test_filter_by_fundamentals_filters_out_when_dv_ttm_nan():
    daily_basic = pd.DataFrame({
        "ts_code": ["A.SH"],
        "trade_date": ["20260101"],
        "pe_ttm": [10.0],
        "dv_ttm": [float("nan")],
        "total_mv": [600_000.0],
        "pb": [1.1],
        "close": [10.0],
    })
    stock_basic = pd.DataFrame({
        "ts_code": ["A.SH"],
        "name": ["Alpha"],
        "industry": ["银行"],
    })
    result = filter_by_fundamentals(daily_basic, stock_basic)
    assert result.empty


def test_filter_by_fundamentals_sorts_by_tushare_dv_ttm_desc():
    daily_basic = pd.DataFrame({
        "ts_code": ["A.SH", "B.SH"],
        "trade_date": ["20260101"] * 2,
        "pe_ttm": [10.0, 10.0],
        "dv_ttm": [4.0, 8.0],
        "total_mv": [600_000.0, 600_000.0],
        "pb": [1.0, 1.0],
        "close": [10.0, 10.0],
    })
    stock_basic = pd.DataFrame({
        "ts_code": ["A.SH", "B.SH"],
        "name": ["Alpha", "Beta"],
        "industry": ["银行", "银行"],
    })
    result = filter_by_fundamentals(daily_basic, stock_basic)
    assert result["ts_code"].tolist() == ["B.SH", "A.SH"]
    assert result.iloc[0]["dv_ttm"] == 8.0
    assert result.iloc[1]["dv_ttm"] == 4.0


def _history_with_ratio(ts_code: str, trade_date: str, ratio: float) -> pd.DataFrame:
    # 构造120天收盘价固定为100，最后一天收盘价 = 100 * ratio，使 MA120≈100
    dates = [f"2025{str(i).zfill(4)}" for i in range(1, 121)]
    closes = [100.0] * 119 + [100.0 * ratio]
    dates.append(trade_date)
    closes.append(100.0 * ratio)
    return pd.DataFrame({"ts_code": [ts_code] * len(dates), "trade_date": dates, "close": closes})


def test_apply_ma120_signal_keeps_mid_band_with_empty_signal():
    candidates = pd.DataFrame({
        "ts_code": ["LOW.SH", "HIGH.SH", "MID.SH"],
        "dv_ttm": [4.0, 4.0, 4.0],
    })
    history = pd.concat([
        _history_with_ratio("LOW.SH", "20260601", 0.80),
        _history_with_ratio("HIGH.SH", "20260601", 1.30),
        _history_with_ratio("MID.SH", "20260601", 1.00),
    ], ignore_index=True)

    result = apply_ma120_signal(candidates, history, "20260601")

    assert set(result["ts_code"]) == {"LOW.SH", "HIGH.SH", "MID.SH"}
    assert result[result["ts_code"] == "LOW.SH"]["ma120_signal"].iloc[0] == "破位低估"
    assert result[result["ts_code"] == "HIGH.SH"]["ma120_signal"].iloc[0] == "强势突破"
    assert result[result["ts_code"] == "MID.SH"]["ma120_signal"].iloc[0] == ""


def test_apply_ma120_signal_keeps_candidate_when_only_mid_band():
    candidates = pd.DataFrame({"ts_code": ["MID.SH"], "dv_ttm": [4.0]})
    history = _history_with_ratio("MID.SH", "20260601", 1.00)
    result = apply_ma120_signal(candidates, history, "20260601")
    assert result["ts_code"].tolist() == ["MID.SH"]
    assert result["ma120_signal"].iloc[0] == ""


def test_apply_ma120_signal_keeps_candidates_when_history_empty():
    candidates = pd.DataFrame({"ts_code": ["A.SH"], "dv_ttm": [4.0]})
    result = apply_ma120_signal(candidates, pd.DataFrame(), "20260601")
    assert result["ts_code"].tolist() == ["A.SH"]
    assert result["ma120_signal"].iloc[0] == ""


def test_apply_ma120_signal_keeps_candidate_without_quotes():
    candidates = pd.DataFrame({
        "ts_code": ["HAS.SH", "NO.SH"],
        "dv_ttm": [4.0, 5.0],
    })
    history = _history_with_ratio("HAS.SH", "20260601", 0.80)
    result = apply_ma120_signal(candidates, history, "20260601")
    assert set(result["ts_code"]) == {"HAS.SH", "NO.SH"}
    assert result[result["ts_code"] == "HAS.SH"]["ma120_signal"].iloc[0] == "破位低估"
    assert result[result["ts_code"] == "NO.SH"]["ma120_signal"].iloc[0] == ""
