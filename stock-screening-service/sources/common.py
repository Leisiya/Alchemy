from datetime import date, datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import pandas as pd

CN_TZ = ZoneInfo("Asia/Shanghai")
HTTP_TIMEOUT_SECONDS = 15
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)

_EXCHANGE_BY_SUFFIX = {"SH": "SSE", "SZ": "SZSE", "BJ": "BSE"}


class DataNotReady(Exception):
    """The source has no data for this date yet (e.g. before market close)."""


class Unsupported(Exception):
    """The source cannot serve this kind of query (e.g. a past-date snapshot)."""


def now_cn() -> datetime:
    return datetime.now(CN_TZ)


def today_cn() -> str:
    return now_cn().strftime("%Y%m%d")


def to_iso(day: str) -> str:
    return f"{day[:4]}-{day[4:6]}-{day[6:8]}"


def from_iso(value) -> str:
    return str(value)[:10].replace("-", "")


def parse_day(day: str) -> date:
    return datetime.strptime(day, "%Y%m%d").date()


def num(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value in ("", "-", "--"):
            return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return None if pd.isna(result) else result


def positive(value) -> Optional[float]:
    """Tushare leaves PE empty for loss-making companies; mirror that."""
    value = num(value)
    return value if value is not None and value > 0 else None


def scaled(value, factor: float) -> Optional[float]:
    value = num(value)
    return None if value is None else round(value * factor, 4)


# ── stock codes: Tushare 600000.SH / Tencent & Sina sh600000 / BaoStock sh.600000 ──

def ts_code_from_symbol(symbol: str) -> str:
    symbol = str(symbol)
    if symbol.startswith("6"):
        return f"{symbol}.SH"
    if symbol.startswith(("0", "3")):
        return f"{symbol}.SZ"
    if symbol.startswith(("4", "8", "92")):
        return f"{symbol}.BJ"
    return f"{symbol}.SH"


def to_prefixed(ts_code: str) -> str:
    symbol, suffix = ts_code.split(".")
    return suffix.lower() + symbol


def from_prefixed(code: str) -> str:
    return f"{code[2:]}.{code[:2].upper()}"


def exchange_of(ts_code: str) -> Optional[str]:
    return _EXCHANGE_BY_SUFFIX.get(ts_code.rsplit(".", 1)[-1])


# ── shared row builders ──

def calendar_frame(
    open_days: list[str],
    exchange: str = "SSE",
    end_date: Optional[str] = None,
    limit: Optional[int] = None,
    start_date: Optional[str] = None,
) -> pd.DataFrame:
    """Trading days in Tushare trade_cal shape: newest first, like Tushare returns them."""
    days = sorted(set(open_days))
    previous = {day: days[i - 1] if i > 0 else None for i, day in enumerate(days)}
    picked = [d for d in days if (not end_date or d <= end_date) and (not start_date or d >= start_date)]
    if limit:
        picked = picked[-int(limit):]
    rows = [
        {"exchange": exchange, "cal_date": day, "is_open": "1", "pretrade_date": previous[day]}
        for day in reversed(picked)
    ]
    return pd.DataFrame(rows, columns=["exchange", "cal_date", "is_open", "pretrade_date"])


def with_price_changes(rows: list[dict]) -> list[dict]:
    """Fill pre_close / change / pct_chg from consecutive closes (first row has no previous close)."""
    rows = sorted(rows, key=lambda row: row["trade_date"])
    previous_close = None
    for row in rows:
        if row.get("pre_close") is None:
            row["pre_close"] = previous_close
        close, pre_close = row.get("close"), row["pre_close"]
        has_both = close is not None and bool(pre_close)
        if row.get("change") is None:
            row["change"] = round(close - pre_close, 4) if has_both else None
        if row.get("pct_chg") is None:
            row["pct_chg"] = round((close - pre_close) / pre_close * 100, 4) if has_both else None
        previous_close = close
    return rows


def recent_quarter_ends(end: date, count: int) -> list[str]:
    """The latest `count` quarter-end dates on or before `end`, newest first, as YYYY-MM-DD."""
    year, quarter = end.year, (end.month - 1) // 3 + 1
    result = []
    while len(result) < count:
        quarter_end = date(year, quarter * 3, 31 if quarter in (1, 4) else 30)
        if quarter_end <= end:
            result.append(quarter_end.isoformat())
        quarter -= 1
        if quarter == 0:
            year, quarter = year - 1, 4
    return result


def days_before(day: str, days: int) -> str:
    return (parse_day(day) - timedelta(days=days)).strftime("%Y%m%d")
