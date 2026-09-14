from unittest.mock import MagicMock

import pandas as pd

from db.repositories import fetch_fina_indicator
from pipeline.roe import attach_candidate_roe, pick_latest_roe


class _FinaPkStore:
    """In-memory stock_fina_indicator with PK (ts_code, end_date) last-write-wins."""

    def __init__(self):
        self._rows = {}

    def conn(self):
        store = self

        class Cursor:
            def __init__(self):
                self._codes = ()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def executemany(self, sql, data):
                for ts_code, ann_date, end_date, roe, update_flag in data:
                    store._rows[(ts_code, end_date)] = {
                        "ts_code": ts_code,
                        "ann_date": ann_date,
                        "end_date": end_date,
                        "roe": roe,
                        "update_flag": update_flag,
                    }

            def execute(self, sql, params):
                self._codes = params

            def fetchall(self):
                return [
                    dict(row)
                    for (code, _), row in store._rows.items()
                    if code in self._codes
                ]

        class Conn:
            def cursor(self):
                return Cursor()

        return Conn()


def test_pick_latest_roe_selects_latest_end_date_announced_on_or_before_trade_date():
    rows = [
        {"ts_code": "A.SH", "ann_date": "20231030", "end_date": "20230930", "roe": 6.0, "update_flag": "1"},
        {"ts_code": "A.SH", "ann_date": "20260420", "end_date": "20260331", "roe": 8.5, "update_flag": "1"},
        {"ts_code": "A.SH", "ann_date": "20260120", "end_date": "20251231", "roe": 7.0, "update_flag": "1"},
    ]
    assert pick_latest_roe(rows, "20260722") == 8.5


def test_pick_latest_roe_prefers_update_flag_1_for_same_end_date():
    rows = [
        {"ts_code": "A.SH", "ann_date": "20260420", "end_date": "20260331", "roe": 8.0, "update_flag": "0"},
        {"ts_code": "A.SH", "ann_date": "20260425", "end_date": "20260331", "roe": 8.5, "update_flag": "1"},
    ]
    assert pick_latest_roe(rows, "20260722") == 8.5


def test_pick_latest_roe_ignores_rows_with_ann_date_after_trade_date():
    rows = [
        {"ts_code": "A.SH", "ann_date": "20260801", "end_date": "20260630", "roe": 12.0, "update_flag": "1"},
        {"ts_code": "A.SH", "ann_date": "20260420", "end_date": "20260331", "roe": 8.5, "update_flag": "1"},
    ]
    assert pick_latest_roe(rows, "20260722") == 8.5


def _conn_with_cursor():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor


def test_attach_candidate_roe_skips_tushare_when_cache_has_qualifying_period():
    conn, cursor = _conn_with_cursor()
    cursor.fetchall.return_value = [
        {"ts_code": "A.SH", "ann_date": "20260420", "end_date": "20260331", "roe": 8.5, "update_flag": "1"},
    ]
    pro = MagicMock()
    result = attach_candidate_roe(conn, pro, ["A.SH"], "20260722")
    assert result == {"A.SH": 8.5}
    pro.fina_indicator.assert_not_called()
    sql, params = cursor.execute.call_args[0]
    assert "stock_fina_indicator" in sql
    assert params == ("A.SH",)


def test_attach_candidate_roe_missing_or_tushare_error_is_none_others_still_return():
    conn, cursor = _conn_with_cursor()
    cursor.fetchall.return_value = []
    pro = MagicMock()

    def fina_indicator(ts_code, fields):
        if ts_code == "FAIL.SH":
            raise RuntimeError("tushare down")
        if ts_code == "EMPTY.SH":
            return pd.DataFrame()
        return pd.DataFrame(
            [
                {
                    "ts_code": ts_code,
                    "ann_date": "20260420",
                    "end_date": "20260331",
                    "roe": 9.1,
                    "update_flag": "1",
                }
            ]
        )

    pro.fina_indicator.side_effect = fina_indicator
    result = attach_candidate_roe(conn, pro, ["FAIL.SH", "EMPTY.SH", "OK.SH"], "20260722")
    assert result["FAIL.SH"] is None
    assert result["EMPTY.SH"] is None
    assert result["OK.SH"] == 9.1


def test_attach_candidate_roe_upsert_fetch_pick_keeps_update_flag_1_roe():
    store = _FinaPkStore()
    conn = store.conn()
    pro = MagicMock()
    pro.fina_indicator.return_value = pd.DataFrame(
        [
            {
                "ts_code": "A.SH",
                "ann_date": "20260425",
                "end_date": "20260331",
                "roe": 8.5,
                "update_flag": "1",
            },
            {
                "ts_code": "A.SH",
                "ann_date": "20260420",
                "end_date": "20260331",
                "roe": 8.0,
                "update_flag": "0",
            },
        ]
    )
    attach_candidate_roe(conn, pro, ["A.SH"], "20260722")
    cached = fetch_fina_indicator(conn, ["A.SH"])
    assert pick_latest_roe(cached, "20260722") == 8.5


def test_attach_candidate_roe_upsert_does_not_overwrite_announced_flag0_with_unannounced_flag1():
    store = _FinaPkStore()
    conn = store.conn()
    pro = MagicMock()
    pro.fina_indicator.return_value = pd.DataFrame(
        [
            {
                "ts_code": "A.SH",
                "ann_date": "20260801",
                "end_date": "20260331",
                "roe": 8.5,
                "update_flag": "1",
            },
            {
                "ts_code": "A.SH",
                "ann_date": "20260420",
                "end_date": "20260331",
                "roe": 8.0,
                "update_flag": "0",
            },
        ]
    )
    result = attach_candidate_roe(conn, pro, ["A.SH"], "20260722")
    cached = fetch_fina_indicator(conn, ["A.SH"])
    assert result["A.SH"] == 8.0
    assert pick_latest_roe(cached, "20260722") == 8.0
    assert len(cached) == 1
    assert cached[0]["roe"] == 8.0
    assert str(cached[0]["update_flag"]) == "0"
