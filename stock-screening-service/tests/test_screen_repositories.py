from datetime import datetime
from unittest.mock import MagicMock

from db import screen_repositories as repo


def test_persist_success_inserts_when_no_existing_run():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    cursor.fetchone.return_value = None
    cursor.lastrowid = 42

    run_id = repo.persist_success(
        conn,
        {
            "strategy_code": "HIGH_DIVIDEND_MA120",
            "trade_date": "20260722",
            "total_count": 1,
            "low_count": 1,
            "high_count": 0,
            "started_at": datetime(2026, 7, 22, 10, 0, 0),
            "finished_at": datetime(2026, 7, 22, 10, 1, 0),
        },
        [
            {
                "strategy_code": "HIGH_DIVIDEND_MA120",
                "trade_date": "20260722",
                "ts_code": "601288.SH",
                "name": "农业银行",
                "industry": "银行",
                "pe_ttm": 5.0,
                "pb": 0.5,
                "dv_ttm": 5.0,
                "total_mv_yi": 1000.0,
                "close_price": 4.0,
                "ma120": 4.5,
                "price_ma120_ratio": 0.89,
                "ma120_signal": "破位低估",
            }
        ],
    )
    assert run_id == 42
    executed = " ".join(str(c.args[0]).lower() for c in cursor.execute.call_args_list)
    assert "insert into stock_screen_run" in executed
    assert "insert into stock_screen_result" in executed


def test_persist_success_updates_and_deletes_old_results():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    cursor.fetchone.return_value = {"run_id": 7}

    run_id = repo.persist_success(
        conn,
        {
            "strategy_code": "HIGH_DIVIDEND_MA120",
            "trade_date": "20260722",
            "total_count": 0,
            "low_count": 0,
            "high_count": 0,
            "started_at": datetime(2026, 7, 22, 10, 0, 0),
            "finished_at": datetime(2026, 7, 22, 10, 1, 0),
        },
        [],
    )
    assert run_id == 7
    executed = " ".join(str(c.args[0]).lower() for c in cursor.execute.call_args_list)
    assert "update stock_screen_run" in executed
    assert "delete from stock_screen_result" in executed


def test_persist_success_insert_includes_roe_between_pb_and_dv_ttm():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    cursor.fetchone.return_value = None
    cursor.lastrowid = 42

    repo.persist_success(
        conn,
        {
            "strategy_code": "HIGH_DIVIDEND_MA120",
            "trade_date": "20260722",
            "total_count": 1,
            "low_count": 1,
            "high_count": 0,
            "started_at": datetime(2026, 7, 22, 10, 0, 0),
            "finished_at": datetime(2026, 7, 22, 10, 1, 0),
        },
        [
            {
                "strategy_code": "HIGH_DIVIDEND_MA120",
                "trade_date": "20260722",
                "ts_code": "601288.SH",
                "name": "农业银行",
                "industry": "银行",
                "pe_ttm": 5.0,
                "pb": 0.5,
                "roe": 8.5,
                "dv_ttm": 5.0,
                "total_mv_yi": 1000.0,
                "close_price": 4.0,
                "ma120": 4.5,
                "price_ma120_ratio": 0.89,
                "ma120_signal": "破位低估",
            }
        ],
    )
    insert_calls = [
        call.args for call in cursor.execute.call_args_list
        if isinstance(call.args[0], str) and "insert into stock_screen_result" in call.args[0].lower()
    ]
    assert insert_calls, "expected INSERT into stock_screen_result"
    sql, params = insert_calls[0]
    sql_lower = sql.lower()
    assert "roe" in sql_lower
    pb_pos = sql_lower.index("pb")
    roe_pos = sql_lower.index("roe")
    dv_pos = sql_lower.index("dv_ttm")
    assert pb_pos < roe_pos < dv_pos
    assert 8.5 in params


def test_persist_failure_inserts_failed_run_and_truncates_message():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    cursor.lastrowid = 9
    long_msg = "x" * 1200
    run_id = repo.persist_failure(
        conn,
        "HIGH_DIVIDEND_MA120",
        "20260722",
        long_msg,
        datetime(2026, 7, 22, 10, 0, 0),
        datetime(2026, 7, 22, 10, 0, 1),
    )
    assert run_id == 9
    args = cursor.execute.call_args[0]
    assert any(isinstance(p, str) and len(p) <= 1000 for p in args[1])
