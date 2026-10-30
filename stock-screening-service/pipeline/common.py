from datetime import datetime
from typing import Optional

import pandas as pd

EXCHANGE = "SSE"
LOOKBACK_DAYS = 125


def iso_now() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def safe_float(value):
    if value is None or pd.isna(value):
        return None
    return float(value)


def ensure_trade_date(value: Optional[str], pro) -> str:
    if value:
        return value
    today = datetime.now().strftime("%Y%m%d")
    cal = pro.trade_cal(exchange=EXCHANGE, end_date=today, is_open="1", limit=1)
    if cal is None or cal.empty:
        raise ValueError("Unable to determine latest trade date")
    return str(cal["cal_date"].iloc[0])
