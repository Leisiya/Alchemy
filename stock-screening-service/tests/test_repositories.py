from unittest.mock import MagicMock

from db import repositories as repo


def make_conn_with_cursor():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor


def test_has_synced_returns_true_when_row_found():
    conn, cursor = make_conn_with_cursor()
    cursor.fetchone.return_value = {"sync_id": 1}
    assert repo.has_synced(conn, "DAILY_BASIC", "20260601") is True
    cursor.execute.assert_called_once()
    sql, params = cursor.execute.call_args[0]
    assert "stock_data_sync_log" in sql
    assert "row_count" in sql
    assert params == ("DAILY_BASIC", "20260601", "0")


def test_has_synced_returns_false_when_no_row():
    conn, cursor = make_conn_with_cursor()
    cursor.fetchone.return_value = None
    assert repo.has_synced(conn, "DAILY_BASIC", "20260601") is False


def test_record_sync_inserts_expected_row():
    conn, cursor = make_conn_with_cursor()
    repo.record_sync(conn, "DAILY_BASIC", "20260601", 4500, "0")
    sql, params = cursor.execute.call_args[0]
    assert "insert into stock_data_sync_log" in sql.lower()
    assert params[0:4] == ("DAILY_BASIC", "20260601", 4500, "0")


def test_upsert_daily_quote_calls_executemany_with_all_rows():
    conn, cursor = make_conn_with_cursor()
    rows = [
        {"ts_code": "A.SH", "trade_date": "20260601", "open": 1.0, "high": 1.2,
         "low": 0.9, "close": 1.1, "pre_close": 1.0, "change": 0.1, "pct_chg": 10.0,
         "vol": 100.0, "amount": 110.0, "ah_vol": None, "ah_amount": None},
    ]
    count = repo.upsert_daily_quote(conn, rows)
    assert count == 1
    cursor.executemany.assert_called_once()
    sql, data = cursor.executemany.call_args[0]
    assert "stock_daily_quote" in sql
    assert data[0][0] == "A.SH"


def test_upsert_daily_quote_returns_zero_for_empty_rows():
    conn, cursor = make_conn_with_cursor()
    assert repo.upsert_daily_quote(conn, []) == 0
    cursor.executemany.assert_not_called()


def test_upsert_converts_nan_to_none():
    import math

    conn, cursor = make_conn_with_cursor()
    rows = [
        {"ts_code": "A.SH", "trade_date": "20260601", "open": 1.0, "high": 1.2,
         "low": 0.9, "close": 1.1, "pre_close": 1.0, "change": 0.1, "pct_chg": 10.0,
         "vol": float("nan"), "amount": 110.0, "ah_vol": float("nan"), "ah_amount": None},
    ]
    repo.upsert_daily_quote(conn, rows)
    data = cursor.executemany.call_args[0][1]
    # vol and ah_vol indices in columns list
    assert data[0][9] is None
    assert data[0][11] is None
    assert not any(isinstance(v, float) and math.isnan(v) for v in data[0])


def test_upsert_fina_indicator_writes_stock_fina_indicator():
    conn, cursor = make_conn_with_cursor()
    rows = [
        {
            "ts_code": "A.SH",
            "ann_date": "20260420",
            "end_date": "20260331",
            "roe": 8.5,
            "update_flag": "1",
        },
    ]
    count = repo.upsert_fina_indicator(conn, rows)
    assert count == 1
    cursor.executemany.assert_called_once()
    sql, data = cursor.executemany.call_args[0]
    assert "stock_fina_indicator" in sql
    assert data[0][0] == "A.SH"
    assert data[0][2] == "20260331"
    update_clause = sql.lower().split("on duplicate key update", 1)[1]
    assert "`end_date`=values(`end_date`)" not in update_clause
    assert "end_date=values(end_date)" not in update_clause.replace("`", "")
    assert "`ann_date`=values(`ann_date`)" in update_clause


def test_fetch_daily_basic_selects_close():
    conn, cursor = make_conn_with_cursor()
    cursor.fetchall.return_value = [
        {
            "ts_code": "A.SH",
            "trade_date": "20260601",
            "pe_ttm": 10.0,
            "dv_ttm": 4.0,
            "total_mv": 600000.0,
            "pb": 1.0,
            "close": 9.5,
        },
    ]
    df = repo.fetch_daily_basic(conn, "20260601")
    sql, params = cursor.execute.call_args[0]
    assert "close" in sql
    assert params == ("20260601",)
    assert df.iloc[0]["close"] == 9.5
