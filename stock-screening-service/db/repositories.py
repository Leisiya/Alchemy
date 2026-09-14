from datetime import datetime

import pandas as pd


def has_synced(conn, dataset: str, trade_date: str) -> bool:
    with conn.cursor() as cursor:
        cursor.execute(
            "select sync_id from stock_data_sync_log where dataset=%s and trade_date=%s and status=%s and row_count > 0 limit 1",
            (dataset, trade_date, "0"),
        )
        return cursor.fetchone() is not None


def record_sync(conn, dataset: str, trade_date: str, row_count: int, status: str, error_message: str = "") -> None:
    now = datetime.now()
    with conn.cursor() as cursor:
        cursor.execute(
            "insert into stock_data_sync_log "
            "(dataset, trade_date, row_count, status, error_message, started_at, finished_at, create_time) "
            "values (%s,%s,%s,%s,%s,%s,%s,%s) "
            "on duplicate key update row_count=%s, error_message=%s, finished_at=%s",
            (dataset, trade_date, row_count, status, error_message[:1000], now, now, now,
             row_count, error_message[:1000], now),
        )


def _quote_col(col: str) -> str:
    # MySQL reserved words (e.g. `change`) must be backticked in DDL/DML
    return f"`{col}`"


def _sql_value(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


_DEFAULT_SKIP_UPDATE_COLS = frozenset(
    ("ts_code", "trade_date", "exchange", "cal_date", "end_date")
)


def _upsert(
    conn,
    table: str,
    columns: list[str],
    rows: list[dict],
    *,
    skip_update_cols: frozenset[str] = _DEFAULT_SKIP_UPDATE_COLS,
) -> int:
    if not rows:
        return 0
    placeholders = ", ".join(["%s"] * len(columns))
    quoted = [_quote_col(col) for col in columns]
    updates = ", ".join(
        f"{_quote_col(col)}=values({_quote_col(col)})"
        for col in columns
        if col not in skip_update_cols
    )
    sql = (
        f"insert into {table} ({', '.join(quoted)}) values ({placeholders}) "
        f"on duplicate key update {updates}"
    )
    data = [tuple(_sql_value(row.get(col)) for col in columns) for row in rows]
    with conn.cursor() as cursor:
        cursor.executemany(sql, data)
    return len(rows)


def upsert_stock_basic(conn, rows: list[dict]) -> int:
    columns = ["ts_code", "symbol", "name", "area", "industry", "fullname", "enname", "cnspell",
               "market", "exchange", "curr_type", "list_status", "list_date", "delist_date",
               "is_hs", "act_name", "act_ent_type"]
    return _upsert(conn, "stock_basic", columns, rows)


def upsert_trade_cal(conn, rows: list[dict]) -> int:
    columns = ["exchange", "cal_date", "is_open", "pretrade_date"]
    return _upsert(conn, "stock_trade_cal", columns, rows)


def upsert_daily_basic(conn, rows: list[dict]) -> int:
    columns = ["ts_code", "trade_date", "close", "turnover_rate", "turnover_rate_f", "volume_ratio",
               "pe", "pe_ttm", "pb", "ps", "ps_ttm", "dv_ratio", "dv_ttm", "total_share",
               "float_share", "free_share", "total_mv", "circ_mv", "limit_status"]
    return _upsert(conn, "stock_daily_basic", columns, rows)


def upsert_daily_quote(conn, rows: list[dict]) -> int:
    columns = ["ts_code", "trade_date", "open", "high", "low", "close", "pre_close",
               "change", "pct_chg", "vol", "amount", "ah_vol", "ah_amount"]
    return _upsert(conn, "stock_daily_quote", columns, rows)


def fetch_stock_basic(conn) -> pd.DataFrame:
    with conn.cursor() as cursor:
        cursor.execute("select ts_code, name, industry from stock_basic")
        rows = cursor.fetchall()
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["ts_code", "name", "industry"])


def _coerce_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def fetch_daily_basic(conn, trade_date: str) -> pd.DataFrame:
    with conn.cursor() as cursor:
        cursor.execute(
            "select ts_code, trade_date, pe_ttm, dv_ttm, total_mv, pb, close "
            "from stock_daily_basic where trade_date=%s",
            (trade_date,),
        )
        rows = cursor.fetchall()
    if not rows:
        return pd.DataFrame(
            columns=["ts_code", "trade_date", "pe_ttm", "dv_ttm", "total_mv", "pb", "close"]
        )
    return _coerce_numeric(
        pd.DataFrame(rows), ["pe_ttm", "dv_ttm", "total_mv", "pb", "close"]
    )


def fetch_daily_quotes(conn, ts_codes: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    if not ts_codes:
        return pd.DataFrame(columns=["ts_code", "trade_date", "close"])
    placeholders = ", ".join(["%s"] * len(ts_codes))
    with conn.cursor() as cursor:
        cursor.execute(
            f"select ts_code, trade_date, close from stock_daily_quote "
            f"where ts_code in ({placeholders}) and trade_date between %s and %s",
            (*ts_codes, start_date, end_date),
        )
        rows = cursor.fetchall()
    if not rows:
        return pd.DataFrame(columns=["ts_code", "trade_date", "close"])
    return _coerce_numeric(pd.DataFrame(rows), ["close"])


def upsert_fina_indicator(conn, rows: list[dict]) -> int:
    columns = ["ts_code", "ann_date", "end_date", "roe", "update_flag"]
    return _upsert(conn, "stock_fina_indicator", columns, rows)


def fetch_fina_indicator(conn, ts_codes: list[str]) -> list[dict]:
    if not ts_codes:
        return []
    placeholders = ", ".join(["%s"] * len(ts_codes))
    with conn.cursor() as cursor:
        cursor.execute(
            f"select ts_code, ann_date, end_date, roe, update_flag "
            f"from stock_fina_indicator where ts_code in ({placeholders})",
            tuple(ts_codes),
        )
        rows = cursor.fetchall()
    return list(rows) if rows else []
