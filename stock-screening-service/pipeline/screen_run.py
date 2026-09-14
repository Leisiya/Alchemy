from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from db.repositories import fetch_daily_basic, fetch_daily_quotes, fetch_stock_basic
from pipeline.common import LOOKBACK_DAYS, ensure_trade_date, iso_now, safe_float
from pipeline.roe import attach_candidate_roe
from strategies.high_dividend_ma120 import (
    STRATEGY_CODE,
    apply_ma120_signal,
    filter_by_fundamentals,
)


def _ma120_signal(value) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in ("", "nan", "none"):
        return ""
    return text


def run_screen(conn, pro, trade_date: Optional[str] = None) -> dict:
    started_at = iso_now()
    resolved = ensure_trade_date(trade_date, pro)

    daily_basic = fetch_daily_basic(conn, resolved)
    stock_basic = fetch_stock_basic(conn)
    candidates = filter_by_fundamentals(daily_basic, stock_basic)

    if candidates.empty:
        final = candidates
    else:
        end_date = resolved
        start_date = (datetime.strptime(resolved, "%Y%m%d") - timedelta(days=LOOKBACK_DAYS * 2)).strftime("%Y%m%d")
        history = fetch_daily_quotes(conn, candidates["ts_code"].tolist(), start_date, end_date)
        final = apply_ma120_signal(candidates, history, resolved)

    roe_by_code = {}
    if not final.empty:
        ts_codes = [str(code) for code in final["ts_code"].tolist()]
        roe_by_code = attach_candidate_roe(conn, pro, ts_codes, resolved)

    results = []
    if not final.empty:
        for _, row in final.iterrows():
            ts_code = str(row["ts_code"])
            results.append(
                {
                    "ts_code": ts_code,
                    "trade_date": resolved,
                    "name": None if pd.isna(row.get("name")) else str(row.get("name")),
                    "industry": None if pd.isna(row.get("industry")) else str(row.get("industry")),
                    "pe_ttm": safe_float(row.get("pe_ttm")),
                    "pb": safe_float(row.get("pb")),
                    "roe": safe_float(roe_by_code.get(ts_code)),
                    "dv_ttm": safe_float(row.get("dv_ttm")),
                    "total_mv_yi": safe_float(row.get("total_mv_yi")),
                    "close_price": safe_float(row.get("close_price")),
                    "ma120": safe_float(row.get("ma120")),
                    "price_ma120_ratio": safe_float(row.get("price_ma120_ratio")),
                    "ma120_signal": _ma120_signal(row.get("ma120_signal")),
                }
            )

    low_count = sum(1 for item in results if item["ma120_signal"] == "破位低估")
    high_count = sum(1 for item in results if item["ma120_signal"] == "强势突破")
    return {
        "strategy_code": STRATEGY_CODE,
        "trade_date": resolved,
        "run_started_at": started_at,
        "run_finished_at": iso_now(),
        "summary": {
            "total_count": len(results),
            "low_count": low_count,
            "high_count": high_count,
        },
        "results": results,
    }
