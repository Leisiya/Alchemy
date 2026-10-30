import logging
from typing import Optional

from db.repositories import fetch_daily_basic, fetch_stock_basic, upsert_daily_quote
from pipeline.common import EXCHANGE, LOOKBACK_DAYS, ensure_trade_date
from strategies.high_dividend_ma120 import filter_by_fundamentals
from sync.daily_basic import sync as daily_basic_sync
from sync.daily_quote import sync as daily_quote_sync
from sync.stock_basic import sync as stock_basic_sync
from sync.trade_cal import sync as trade_cal_sync

logger = logging.getLogger(__name__)


def _has_valuations(conn, trade_date: str) -> bool:
    df = fetch_daily_basic(conn, trade_date)
    return df is not None and not df.empty


def _sync_stock_basic(conn, pro, trade_date: str) -> int:
    try:
        return stock_basic_sync(conn, pro, trade_date)
    except Exception as exc:
        cached = fetch_stock_basic(conn)
        if cached is None or cached.empty:
            raise
        # the stock list barely changes day to day; reuse the cached one rather than fail the run
        logger.warning("股票列表同步失败，沿用库里已有的 %d 只：%s", len(cached), exc)
        return 0


def _backfill_candidate_quotes(conn, pro, trade_date: str, start_date: str) -> int:
    """Fallback when whole-market quotes for some days could not be fetched: pull per-stock
    history for the screening candidates only, which is all MA120 needs."""
    candidates = filter_by_fundamentals(fetch_daily_basic(conn, trade_date), fetch_stock_basic(conn))
    if candidates.empty:
        return 0
    total = 0
    for ts_code in candidates["ts_code"].tolist():
        try:
            df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=trade_date)
        except Exception as exc:
            logger.warning("补 %s 的历史日线失败：%s", ts_code, exc)
            continue
        rows = df.to_dict("records") if df is not None and not df.empty else []
        if rows:
            total += upsert_daily_quote(conn, rows)
            conn.commit()
    logger.info("为 %d 只候选股补了 %d 条日线", len(candidates), total)
    return total


def run_sync(conn, pro, trade_date: Optional[str] = None, lookback_days: int = LOOKBACK_DAYS) -> dict:
    resolved = ensure_trade_date(trade_date, pro)
    days = lookback_days if lookback_days and lookback_days > 0 else LOOKBACK_DAYS

    stock_basic_count = _sync_stock_basic(conn, pro, resolved)
    trade_cal_count = trade_cal_sync(conn, pro, resolved)
    daily_basic_count = daily_basic_sync(conn, pro, resolved)

    cal = pro.trade_cal(
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
    failed_quote_dates = []
    for day in quote_dates:
        try:
            daily_quote_count += daily_quote_sync(conn, pro, day)
        except Exception as exc:
            logger.warning("%s 的全市场日线同步失败：%s", day, exc)
            failed_quote_dates.append(day)

    quote_backfill_count = 0
    if failed_quote_dates:
        quote_backfill_count = _backfill_candidate_quotes(conn, pro, resolved, min(failed_quote_dates))

    return {
        "trade_date": resolved,
        "stock_basic": stock_basic_count,
        "trade_cal": trade_cal_count,
        "daily_basic": daily_basic_count,
        "daily_quote": daily_quote_count,
        "failed_quote_dates": failed_quote_dates,
        "quote_backfill": quote_backfill_count,
    }
