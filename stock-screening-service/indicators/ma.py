from typing import Optional

import pandas as pd


def compute_ma(history: pd.DataFrame, window: int = 120) -> pd.DataFrame:
    result = history.sort_values(["ts_code", "trade_date"]).reset_index(drop=True).copy()
    column = f"ma{window}"
    result[column] = result.groupby("ts_code")["close"].transform(
        lambda values: values.rolling(window=window, min_periods=window).mean()
    )
    return result


def classify_signal(ratio: float, low_threshold: float = 0.88, high_threshold: float = 1.12) -> Optional[str]:
    if ratio < low_threshold:
        return "破位低估"
    if ratio > high_threshold:
        return "强势突破"
    return None
