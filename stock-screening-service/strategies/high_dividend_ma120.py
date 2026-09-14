import pandas as pd

from indicators.ma import compute_ma, classify_signal

STRATEGY_CODE = "HIGH_DIVIDEND_MA120"
MA_WINDOW = 120
PE_TTM_MAX = 20
DV_TTM_MIN = 3.0
TOTAL_MV_MIN = 500_000.0
LOW_THRESHOLD = 0.88
HIGH_THRESHOLD = 1.12


def filter_by_fundamentals(
    daily_basic: pd.DataFrame,
    stock_basic: pd.DataFrame,
) -> pd.DataFrame:
    if daily_basic is None or daily_basic.empty:
        return pd.DataFrame()

    merged = daily_basic.merge(stock_basic, on="ts_code", how="left")
    mask = (
        (merged["pe_ttm"] > 0)
        & (merged["pe_ttm"] < PE_TTM_MAX)
        & (merged["dv_ttm"] > DV_TTM_MIN)
        & (merged["total_mv"] > TOTAL_MV_MIN)
    )
    result = merged.loc[mask].copy()
    if result.empty:
        return result

    result = result.sort_values("dv_ttm", ascending=False).reset_index(drop=True)
    result["total_mv_yi"] = (result["total_mv"] / 10000).round(1)
    return result


def apply_ma120_signal(candidates: pd.DataFrame, history: pd.DataFrame, trade_date: str) -> pd.DataFrame:
    if candidates is None or candidates.empty:
        return pd.DataFrame()

    empty_signal = candidates.copy()
    empty_signal["close_price"] = pd.NA
    empty_signal["ma120"] = pd.NA
    empty_signal["price_ma120_ratio"] = pd.NA
    empty_signal["ma120_signal"] = ""

    if history is None or history.empty:
        return empty_signal.reset_index(drop=True)

    with_ma = compute_ma(history, window=MA_WINDOW)
    ma_column = f"ma{MA_WINDOW}"
    latest = with_ma.loc[
        with_ma["trade_date"] == trade_date, ["ts_code", "close", ma_column]
    ].copy()
    if latest.empty:
        return empty_signal.reset_index(drop=True)

    latest = latest.rename(columns={"close": "close_price", ma_column: "ma120"})
    latest["close_price"] = latest["close_price"].round(2)
    latest["ma120"] = latest["ma120"].round(2)
    latest["price_ma120_ratio"] = (latest["close_price"] / latest["ma120"]).round(4)
    latest["ma120_signal"] = latest["price_ma120_ratio"].apply(
        lambda ratio: classify_signal(ratio, LOW_THRESHOLD, HIGH_THRESHOLD) if pd.notna(ratio) else None
    )
    latest["ma120_signal"] = latest["ma120_signal"].fillna("")

    merged = candidates.merge(
        latest[["ts_code", "close_price", "ma120", "price_ma120_ratio", "ma120_signal"]],
        on="ts_code",
        how="left",
    )
    merged["ma120_signal"] = merged["ma120_signal"].fillna("")
    return merged.reset_index(drop=True)
