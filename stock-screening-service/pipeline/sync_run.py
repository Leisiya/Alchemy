from typing import Optional

from clients.tushare_client import call_with_retry
from db.repositories import fetch_daily_basic
from pipeline.common import EXCHANGE, LOOKBACK_DAYS, ensure_trade_date
from sync.daily_basic import sync as daily_basic_sync
from sync.daily_quote import sync as daily_quote_sync
from sync.stock_basic import sync as stock_basic_sync
from sync.trade_cal import sync as trade_cal_sync


def _has_valuations(conn, trade_date: str) -> bool:
    df = fetch_daily_basic(conn, trade_date)
    return df is not None and not df.empty


def run_sync(conn, pro, trade_date: Optional[str] = None, lookback_days: int = LOOKBACK_DAYS) -> dict:
    resolved = ensure_trade_date(trade_date, pro)
    days = lookback_days if lookback_days and lookback_days > 0 else LOOKBACK_DAYS

    stock_basic_count = stock_basic_sync(conn, pro, resolved)
    trade_cal_count = trade_cal_sync(conn, pro, resolved)
    daily_basic_count = daily_basic_sync(conn, pro, resolved)

    cal = call_with_retry(
        pro.trade_cal,
        exchange=EXCHANGE,
        end_date=resolved,
        is_open="1",
        limit=days,
    )
    trade_dates = [] if cal is None or cal.empty else [str(d) for d in sorted(cal["cal_date"].tolist())]

    if daily_basic_count <= 0 and not _has_valuations(conn, resolved):
        raise ValueError("当日估值数据尚未落地")

    quote_dates = [day for day in trade_dates if day <= resolved]
    daily_quote_count = 0
    for day in quote_dates:
        daily_quote_count += daily_quote_sync(conn, pro, day)

    return {
        "trade_date": resolved,
        "stock_basic": stock_basic_count,
        "trade_cal": trade_cal_count,
        "daily_basic": daily_basic_count,
        "daily_quote": daily_quote_count,
    }
