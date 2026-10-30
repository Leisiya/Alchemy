"""BaoStock (www.baostock.com): free, anonymous login, independent of the web-scraped sources.

Last line of defence: everything is per-stock and slower, and Beijing exchange stocks are not covered.
"""
import contextlib
import io
import re

import pandas as pd

from sources.common import (
    Unsupported,
    calendar_frame,
    days_before,
    exchange_of,
    from_iso,
    num,
    parse_day,
    recent_quarter_ends,
    to_iso,
    today_cn,
)

CALENDAR_LOOKBACK_DAYS = 400
ROE_QUARTERS = 6
_INDUSTRY_CODE_PREFIX = re.compile(r"^[A-Z]\d*")


def _to_baostock(ts_code: str) -> str:
    symbol, suffix = ts_code.split(".")
    if suffix == "BJ":
        raise Unsupported("BaoStock 没有北交所数据")
    return f"{suffix.lower()}.{symbol}"


def _from_baostock(code: str) -> str:
    market, symbol = code.split(".")
    return f"{symbol}.{market.upper()}"


class BaostockSource:
    name = "baostock"

    def __init__(self):
        self._bs = None

    def close(self):
        if self._bs is not None:
            with contextlib.redirect_stdout(io.StringIO()):
                self._bs.logout()
            self._bs = None

    def trade_cal(self, exchange="SSE", end_date=None, is_open="1", limit=None, start_date=None, **_kwargs):
        if str(is_open) != "1":
            raise Unsupported("只取开市日")
        end_date = end_date or today_cn()
        first = start_date or days_before(end_date, CALENDAR_LOOKBACK_DAYS)
        rows = self._rows(self._api().query_trade_dates(start_date=to_iso(first), end_date=to_iso(end_date)))
        days = [from_iso(row["calendar_date"]) for row in rows if row["is_trading_day"] == "1"]
        return calendar_frame(days, exchange, end_date, limit, start_date)

    def stock_basic(self, **_kwargs) -> pd.DataFrame:
        bs = self._api()
        industries = {
            row["code"]: _INDUSTRY_CODE_PREFIX.sub("", row["industry"]) or None
            for row in self._rows(bs.query_stock_industry())
        }
        rows = []
        for row in self._rows(bs.query_stock_basic()):
            if row["type"] != "1" or row["status"] != "1":
                continue
            ts_code = _from_baostock(row["code"])
            rows.append({
                "ts_code": ts_code,
                "symbol": ts_code.split(".")[0],
                "name": row["code_name"],
                "industry": industries.get(row["code"]),
                "exchange": exchange_of(ts_code),
                "list_status": "L",
                "list_date": from_iso(row["ipoDate"]),
            })
        return pd.DataFrame(rows)

    def daily(self, ts_code=None, start_date=None, end_date=None, **_kwargs) -> pd.DataFrame:
        if not ts_code:
            raise Unsupported("BaoStock 只能按股票取历史日线")
        result = self._api().query_history_k_data_plus(
            _to_baostock(ts_code),
            "date,open,high,low,close,preclose,volume,amount,pctChg,tradestatus",
            start_date=to_iso(start_date),
            end_date=to_iso(end_date),
            frequency="d",
            adjustflag="3",  # unadjusted, same as Tushare daily
        )
        rows = []
        for row in self._rows(result):
            if row["tradestatus"] != "1":
                continue
            close, pre_close = num(row["close"]), num(row["preclose"])
            rows.append({
                "ts_code": ts_code,
                "trade_date": from_iso(row["date"]),
                "open": num(row["open"]),
                "high": num(row["high"]),
                "low": num(row["low"]),
                "close": close,
                "pre_close": pre_close,
                "change": None if close is None or pre_close is None else round(close - pre_close, 4),
                "pct_chg": num(row["pctChg"]),
                "vol": None if num(row["volume"]) is None else num(row["volume"]) / 100,
                "amount": None if num(row["amount"]) is None else num(row["amount"]) / 1000,
            })
        return pd.DataFrame(rows)

    def fina_indicator(self, ts_code: str, **_kwargs) -> pd.DataFrame:
        bs, code = self._api(), _to_baostock(ts_code)
        rows = []
        for quarter_end in recent_quarter_ends(parse_day(today_cn()), ROE_QUARTERS):
            year, quarter = int(quarter_end[:4]), int(quarter_end[5:7]) // 3
            for row in self._rows(bs.query_profit_data(code=code, year=year, quarter=quarter)):
                roe = num(row["roeAvg"])
                rows.append({
                    "ts_code": ts_code,
                    "ann_date": from_iso(row["pubDate"]),
                    "end_date": from_iso(row["statDate"]),
                    "roe": None if roe is None else round(roe * 100, 4),  # BaoStock gives a ratio, Tushare a percent
                    "update_flag": "0",
                })
        return pd.DataFrame(rows)

    def _api(self):
        if self._bs is None:
            import baostock as bs

            with contextlib.redirect_stdout(io.StringIO()):  # login prints to stdout
                result = bs.login()
            if result.error_code != "0":
                raise RuntimeError(f"BaoStock 登录失败：{result.error_msg}")
            self._bs = bs
        return self._bs

    @staticmethod
    def _rows(result) -> list[dict]:
        if result.error_code != "0":
            raise RuntimeError(f"BaoStock 查询失败：{result.error_msg}")
        rows = []
        while result.next():
            rows.append(dict(zip(result.fields, result.get_row_data())))
        if result.error_code != "0":
            raise RuntimeError(f"BaoStock 查询失败：{result.error_msg}")
        return rows
