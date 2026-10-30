from db import repositories as repo

DATASET = "DAILY_QUOTE"


def sync(conn, pro, anchor_date: str) -> int:
    if repo.has_synced(conn, DATASET, anchor_date):
        return 0
    try:
        df = pro.daily(
            trade_date=anchor_date,
            fields="ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount",
        )
        rows = df.to_dict("records") if df is not None and not df.empty else []
        if not rows:
            return 0
        row_count = repo.upsert_daily_quote(conn, rows)
        repo.record_sync(conn, DATASET, anchor_date, row_count, "0")
        conn.commit()
        return row_count
    except Exception as exc:
        conn.rollback()
        repo.record_sync(conn, DATASET, anchor_date, 0, "1", str(exc))
        conn.commit()
        raise
