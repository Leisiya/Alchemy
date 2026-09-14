from clients.tushare_client import call_with_retry
from db import repositories as repo

DATASET = "TRADE_CAL"
EXCHANGE = "SSE"
LOOKBACK_DAYS = 125


def sync(conn, pro, anchor_date: str) -> int:
    if repo.has_synced(conn, DATASET, anchor_date):
        return 0
    try:
        df = call_with_retry(
            pro.trade_cal,
            exchange=EXCHANGE,
            end_date=anchor_date,
            is_open="1",
            limit=LOOKBACK_DAYS,
        )
        rows = df.to_dict("records") if df is not None and not df.empty else []
        row_count = repo.upsert_trade_cal(conn, rows)
        repo.record_sync(conn, DATASET, anchor_date, row_count, "0")
        conn.commit()
        return row_count
    except Exception as exc:
        conn.rollback()
        repo.record_sync(conn, DATASET, anchor_date, 0, "1", str(exc))
        conn.commit()
        raise
