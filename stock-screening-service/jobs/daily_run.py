import argparse
import logging
import sys
from datetime import datetime
from typing import Optional

from db.connection import get_connection
from db.repositories import fetch_stock_basic
from db.screen_repositories import find_success_run, persist_failure, persist_success
from pipeline.common import LOOKBACK_DAYS, ensure_trade_date
from pipeline.screen_run import run_screen
from pipeline.sync_run import run_sync
from sources.market_data import build_market_data

STRATEGY_CODE = "HIGH_DIVIDEND_MA120"
logger = logging.getLogger(__name__)


def calendar_today() -> str:
    return datetime.now().strftime("%Y%m%d")


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="Sync market cache and persist screening snapshot")
    parser.add_argument("--trade-date", dest="trade_date", default=None, help="YYYYMMDD")
    parser.add_argument("--lookback-days", dest="lookback_days", type=int, default=LOOKBACK_DAYS)
    parser.add_argument("--skip-sync", dest="skip_sync", action="store_true")
    args = parser.parse_args(argv)

    started_at = datetime.now().replace(microsecond=0)
    trade_date = args.trade_date or started_at.strftime("%Y%m%d")
    conn = None
    pro = None
    try:
        conn = get_connection()
        pro = build_market_data(universe=lambda: fetch_stock_basic(conn)["ts_code"].tolist())
        resolved = ensure_trade_date(args.trade_date, pro)
        today = calendar_today()
        if not args.trade_date and resolved != today:
            logger.info("skip daily_run: resolved trade date %s is not today %s", resolved, today)
            return 0
        if not args.trade_date and find_success_run(conn, STRATEGY_CODE, resolved):
            logger.info("skip daily_run: success run already exists for %s on %s", STRATEGY_CODE, resolved)
            return 0
        trade_date = resolved
        if not args.skip_sync:
            sync_out = run_sync(conn, pro, resolved, args.lookback_days)
            trade_date = sync_out["trade_date"]
            screen_out = run_screen(conn, pro, trade_date)
        else:
            screen_out = run_screen(conn, pro, resolved)
        trade_date = screen_out["trade_date"]
        run = {
            "strategy_code": screen_out["strategy_code"],
            "trade_date": trade_date,
            "total_count": screen_out["summary"]["total_count"],
            "low_count": screen_out["summary"]["low_count"],
            "high_count": screen_out["summary"]["high_count"],
            "started_at": _parse_iso(screen_out["run_started_at"]),
            "finished_at": _parse_iso(screen_out["run_finished_at"]),
        }
        results = []
        for item in screen_out["results"]:
            row = dict(item)
            row["strategy_code"] = screen_out["strategy_code"]
            row["trade_date"] = trade_date
            results.append(row)
        persist_success(conn, run, results)
        logger.info("daily_run done: %s, %d results, sources %s", trade_date, len(results), getattr(pro, "used", {}))
        return 0
    except Exception as exc:
        if (
            not args.trade_date
            and isinstance(exc, ValueError)
            and "当日估值数据尚未落地" in str(exc)
        ):
            logger.info("wait daily_run: %s", exc)
            return 0
        logger.exception("daily_run failed for %s", trade_date)
        finished_at = datetime.now().replace(microsecond=0)
        if conn is not None:
            try:
                persist_failure(conn, STRATEGY_CODE, trade_date, str(exc), started_at, finished_at)
            except Exception:
                pass
        return 1
    finally:
        if pro is not None and hasattr(pro, "close"):
            pro.close()
        if conn is not None and hasattr(conn, "close"):
            conn.close()


if __name__ == "__main__":
    # stdout/stderr end up in the backend log via the Java ProcessBuilder (inheritIO)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [screener] %(name)s - %(message)s")
    sys.exit(main())
