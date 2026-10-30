from db import repositories as repo

DATASET = "STOCK_BASIC"


def sync(conn, pro, anchor_date: str) -> int:
    if repo.has_synced(conn, DATASET, anchor_date):
        return 0
    try:
        df = pro.stock_basic(
            exchange="",
            list_status="L",
            fields="ts_code,symbol,name,area,industry,fullname,enname,cnspell,market,exchange,"
                   "curr_type,list_status,list_date,delist_date,is_hs,act_name,act_ent_type",
        )
        rows = df.to_dict("records") if df is not None and not df.empty else []
        row_count = repo.upsert_stock_basic(conn, rows)
        repo.record_sync(conn, DATASET, anchor_date, row_count, "0")
        conn.commit()
        return row_count
    except Exception as exc:
        conn.rollback()
        repo.record_sync(conn, DATASET, anchor_date, 0, "1", str(exc))
        conn.commit()
        raise
