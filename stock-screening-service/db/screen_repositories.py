from datetime import datetime
from typing import Optional


STATUS_SUCCESS = "0"
STATUS_FAILED = "1"
SYS_USER = "system"


def find_success_run(conn, strategy_code: str, trade_date: str) -> Optional[int]:
    with conn.cursor() as cursor:
        cursor.execute(
            "select run_id from stock_screen_run "
            "where strategy_code=%s and trade_date=%s and status=%s limit 1",
            (strategy_code, trade_date, STATUS_SUCCESS),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        if isinstance(row, dict):
            return int(row["run_id"])
        return int(row[0])


def persist_success(conn, run: dict, results: list[dict]) -> int:
    existing_id = find_success_run(conn, run["strategy_code"], run["trade_date"])
    with conn.cursor() as cursor:
        if existing_id is None:
            cursor.execute(
                "insert into stock_screen_run "
                "(strategy_code, trade_date, status, total_count, low_count, high_count, "
                "error_message, started_at, finished_at, create_by, create_time, update_by, update_time) "
                "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    run["strategy_code"],
                    run["trade_date"],
                    STATUS_SUCCESS,
                    run.get("total_count", 0),
                    run.get("low_count", 0),
                    run.get("high_count", 0),
                    "",
                    run["started_at"],
                    run["finished_at"],
                    SYS_USER,
                    datetime.now(),
                    SYS_USER,
                    datetime.now(),
                ),
            )
            run_id = int(cursor.lastrowid)
        else:
            run_id = existing_id
            cursor.execute(
                "update stock_screen_run set total_count=%s, low_count=%s, high_count=%s, "
                "error_message=%s, started_at=%s, finished_at=%s, update_by=%s, update_time=%s "
                "where run_id=%s",
                (
                    run.get("total_count", 0),
                    run.get("low_count", 0),
                    run.get("high_count", 0),
                    "",
                    run["started_at"],
                    run["finished_at"],
                    SYS_USER,
                    datetime.now(),
                    run_id,
                ),
            )
            cursor.execute("delete from stock_screen_result where run_id=%s", (run_id,))

        for item in results:
            cursor.execute(
                "insert into stock_screen_result "
                "(run_id, strategy_code, trade_date, ts_code, name, industry, pe_ttm, pb, roe, dv_ttm, "
                "total_mv_yi, close_price, ma120, price_ma120_ratio, ma120_signal, create_by, create_time) "
                "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    run_id,
                    item.get("strategy_code", run["strategy_code"]),
                    item.get("trade_date", run["trade_date"]),
                    item["ts_code"],
                    item.get("name") or "",
                    item.get("industry") or "",
                    item.get("pe_ttm"),
                    item.get("pb"),
                    item.get("roe"),
                    item.get("dv_ttm"),
                    item.get("total_mv_yi"),
                    item.get("close_price"),
                    item.get("ma120"),
                    item.get("price_ma120_ratio"),
                    item.get("ma120_signal") or "",
                    SYS_USER,
                    datetime.now(),
                ),
            )
    conn.commit()
    return run_id


def persist_failure(
    conn,
    strategy_code: str,
    trade_date: str,
    error_message: str,
    started_at,
    finished_at,
) -> int:
    message = (error_message or "")[:1000]
    with conn.cursor() as cursor:
        cursor.execute(
            "insert into stock_screen_run "
            "(strategy_code, trade_date, status, total_count, low_count, high_count, "
            "error_message, started_at, finished_at, create_by, create_time, update_by, update_time) "
            "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                strategy_code,
                trade_date,
                STATUS_FAILED,
                0,
                0,
                0,
                message,
                started_at,
                finished_at,
                SYS_USER,
                datetime.now(),
                SYS_USER,
                datetime.now(),
            ),
        )
        run_id = int(cursor.lastrowid)
    conn.commit()
    return run_id
