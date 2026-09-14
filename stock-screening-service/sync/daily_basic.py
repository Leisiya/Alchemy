from clients.tushare_client import call_with_retry
from db import repositories as repo

DATASET = "DAILY_BASIC"


def sync(conn, pro, anchor_date: str) -> int:
    if repo.has_synced(conn, DATASET, anchor_date):
        return 0
    try:
        df = call_with_retry(
            pro.daily_basic,
            trade_date=anchor_date,
            fields="ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,"
                   "pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,free_share,total_mv,circ_mv,limit_status",
        )
        rows = df.to_dict("records") if df is not None and not df.empty else []
        if not rows:
            return 0
        row_count = repo.upsert_daily_basic(conn, rows)
        repo.record_sync(conn, DATASET, anchor_date, row_count, "0")
        conn.commit()
        return row_count
    except Exception as exc:
        conn.rollback()
        repo.record_sync(conn, DATASET, anchor_date, 0, "1", str(exc))
        conn.commit()
        raise
