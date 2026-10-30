"""Eastmoney data center (datacenter-web.eastmoney.com). Free, and serves past dates.

From the Tencent Cloud server, Eastmoney's quote API (push2) drops the connection outright,
but the data center works, so only data-center reports are used here:
  RPT_VALUEANALYSIS_DET  valuation by trade date: close / PE TTM / PB / market cap / industry
  RPT_SHAREBONUS_DET     dividend plans by report period, used to compute the TTM dividend yield
  RPT_LICO_FN_CPD        earnings reports by report period, used for ROE
"""
import re
import time
from collections import defaultdict
from datetime import timedelta
from typing import Optional

import pandas as pd
import requests

from sources.common import (
    HTTP_TIMEOUT_SECONDS,
    USER_AGENT,
    DataNotReady,
    Unsupported,
    exchange_of,
    from_iso,
    num,
    parse_day,
    positive,
    recent_quarter_ends,
    scaled,
    to_iso,
    today_cn,
)

URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
HEADERS = {"User-Agent": USER_AGENT, "Referer": "https://data.eastmoney.com/"}
PAGE_SIZE = 5000
REQUEST_INTERVAL_SECONDS = 0.2
VALUATION_COLUMNS = (
    "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,BOARD_NAME,TRADE_DATE,CLOSE_PRICE,CHANGE_RATE,"
    "PE_TTM,PE_LAR,PB_MRQ,PS_TTM,TOTAL_MARKET_CAP,NOTLIMITED_MARKETCAP_A,TOTAL_SHARES,FREE_SHARES_A"
)
# a dividend ex-dated within the last year can belong to a report period ~18 months back; fetch 2 years
DIVIDEND_PERIODS = 8
ROE_PERIODS = 3
_BOARD_LEVEL_SUFFIX = re.compile(r"[ⅠⅡⅢ]+$")


class EastmoneySource:
    name = "eastmoney"

    def __init__(self, session=None):
        self._session = session or requests.Session()
        self._valuations: dict[str, list[dict]] = {}
        self._bonus_by_period: dict[str, list[dict]] = {}
        self._roe_by_code: Optional[dict[str, list[dict]]] = None

    def stock_basic(self, **_kwargs) -> pd.DataFrame:
        latest = self._latest_valuation_date()
        rows = [
            {
                "ts_code": item["SECUCODE"],
                "symbol": item["SECURITY_CODE"],
                "name": item["SECURITY_NAME_ABBR"],
                "industry": _BOARD_LEVEL_SUFFIX.sub("", item.get("BOARD_NAME") or "") or None,
                "exchange": exchange_of(item["SECUCODE"]),
                "list_status": "L",
            }
            for item in self._valuation(latest)
        ]
        return pd.DataFrame(rows)

    def daily_basic(self, trade_date: str, **_kwargs) -> pd.DataFrame:
        valuations = self._valuation(trade_date)
        dividend_ps = self._dividend_per_share_ttm(trade_date)
        rows = []
        for item in valuations:
            ts_code, close = item["SECUCODE"], num(item.get("CLOSE_PRICE"))
            cash = dividend_ps.get(ts_code)
            rows.append({
                "ts_code": ts_code,
                "trade_date": trade_date,
                "close": close,
                "pe": positive(item.get("PE_LAR")),
                "pe_ttm": positive(item.get("PE_TTM")),
                "pb": num(item.get("PB_MRQ")),
                "ps_ttm": num(item.get("PS_TTM")),
                "dv_ttm": round(cash / close * 100, 4) if cash and close else None,
                "total_share": scaled(item.get("TOTAL_SHARES"), 1e-4),
                "float_share": scaled(item.get("FREE_SHARES_A"), 1e-4),
                "total_mv": scaled(item.get("TOTAL_MARKET_CAP"), 1e-4),
                "circ_mv": scaled(item.get("NOTLIMITED_MARKETCAP_A"), 1e-4),
            })
        return pd.DataFrame(rows)

    def daily(self, trade_date=None, ts_code=None, **_kwargs) -> pd.DataFrame:
        if ts_code or not trade_date:
            raise Unsupported("东方财富数据中心只能按交易日取全市场收盘价")
        # close-only rows: enough for MA120, which is all the screener reads from stock_daily_quote
        rows = [
            {
                "ts_code": item["SECUCODE"],
                "trade_date": trade_date,
                "close": num(item.get("CLOSE_PRICE")),
                "pct_chg": num(item.get("CHANGE_RATE")),
            }
            for item in self._valuation(trade_date)
        ]
        return pd.DataFrame(rows)

    def fina_indicator(self, ts_code: str, **_kwargs) -> pd.DataFrame:
        if self._roe_by_code is None:
            self._roe_by_code = self._load_roe()
        return pd.DataFrame(self._roe_by_code.get(ts_code, []))

    def _valuation(self, trade_date: str) -> list[dict]:
        if trade_date not in self._valuations:
            rows = self._query(
                "RPT_VALUEANALYSIS_DET", VALUATION_COLUMNS, f"(TRADE_DATE='{to_iso(trade_date)}')", "SECUCODE"
            )
            if not rows:
                raise DataNotReady(f"{trade_date} 的估值数据还没出")
            self._valuations[trade_date] = rows
        return self._valuations[trade_date]

    def _latest_valuation_date(self) -> str:
        body = self._request({
            "reportName": "RPT_VALUEANALYSIS_DET",
            "columns": "TRADE_DATE",
            "pageNumber": 1,
            "pageSize": 1,
            "sortColumns": "TRADE_DATE",
            "sortTypes": -1,
        })
        data = (body.get("result") or {}).get("data") or []
        if not data:
            raise RuntimeError("东方财富估值报表没有数据")
        return from_iso(data[0]["TRADE_DATE"])

    def _dividend_per_share_ttm(self, trade_date: str) -> dict[str, float]:
        """Pre-tax cash dividend per current share with an ex-date in the 12 months up to trade_date.

        Cash paid before a bonus-share issue is divided by the issue ratio so it is per current share.
        Compared with Tencent's TTM yield on 2026-10-30 this was within 5% for 95% of stocks, and only
        42 of ~5,500 landed on the other side of the 3% screening line; the rest is vendor disagreement.
        """
        end = parse_day(trade_date)
        end_iso, year_ago = end.isoformat(), (end - timedelta(days=365)).isoformat()
        events: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
        for period in recent_quarter_ends(end, DIVIDEND_PERIODS):
            for item in self._bonus(period):
                ex_date = str(item.get("EX_DIVIDEND_DATE") or "")[:10]
                cash = (num(item.get("PRETAX_BONUS_RMB")) or 0) / 10
                bonus_per_ten = num(item.get("BONUS_IT_RATIO")) or 0
                if ex_date and ex_date <= end_iso and (cash or bonus_per_ten):
                    events[item["SECUCODE"]].append((ex_date, cash, bonus_per_ten))
        totals = {}
        for ts_code, items in events.items():
            total = 0.0
            for ex_date, cash, _ in items:
                if not cash or ex_date <= year_ago:
                    continue
                share_factor = 1.0
                for other_ex_date, _, bonus_per_ten in items:
                    if bonus_per_ten and other_ex_date >= ex_date:
                        share_factor *= 1 + bonus_per_ten / 10
                total += cash / share_factor
            if total:
                totals[ts_code] = total
        return totals

    def _bonus(self, period: str) -> list[dict]:
        if period not in self._bonus_by_period:
            self._bonus_by_period[period] = self._query(
                "RPT_SHAREBONUS_DET",
                "SECUCODE,PRETAX_BONUS_RMB,BONUS_IT_RATIO,EX_DIVIDEND_DATE",
                f"(REPORT_DATE='{period}')",
                "SECUCODE",
            )
        return self._bonus_by_period[period]

    def _load_roe(self) -> dict[str, list[dict]]:
        latest: dict[tuple[str, str], dict] = {}
        for period in recent_quarter_ends(parse_day(today_cn()), ROE_PERIODS):
            for item in self._query(
                "RPT_LICO_FN_CPD",
                "SECUCODE,NOTICE_DATE,REPORTDATE,WEIGHTAVG_ROE",
                f"(REPORTDATE='{period}')",
                "SECUCODE",
            ):
                row = {
                    "ts_code": item["SECUCODE"],
                    "ann_date": from_iso(item.get("NOTICE_DATE") or ""),
                    "end_date": from_iso(item["REPORTDATE"]),
                    "roe": num(item.get("WEIGHTAVG_ROE")),
                    "update_flag": "0",
                }
                key = (row["ts_code"], row["end_date"])
                # the report lists revisions as separate rows; keep the latest announcement
                if key not in latest or row["ann_date"] > latest[key]["ann_date"]:
                    latest[key] = row
        by_code: dict[str, list[dict]] = defaultdict(list)
        for row in latest.values():
            by_code[row["ts_code"]].append(row)
        return by_code

    def _query(self, report: str, columns: str, filter_: str, sort_column: str) -> list[dict]:
        rows, page, pages = [], 1, 1
        while page <= pages:
            body = self._request({
                "reportName": report,
                "columns": columns,
                "filter": filter_,
                "pageNumber": page,
                "pageSize": PAGE_SIZE,
                "sortColumns": sort_column,
                "sortTypes": 1,
            })
            result = body.get("result")
            if not result:
                return rows
            rows.extend(result.get("data") or [])
            pages = int(result.get("pages") or 1)
            page += 1
        return rows

    def _request(self, params: dict) -> dict:
        resp = self._session.get(URL, params=params, headers=HEADERS, timeout=HTTP_TIMEOUT_SECONDS)
        resp.raise_for_status()
        body = resp.json()
        time.sleep(REQUEST_INTERVAL_SECONDS)
        # an empty result comes back as success=false with "返回数据为空"; anything else is a real error
        if not body.get("success") and "为空" not in str(body.get("message")):
            raise RuntimeError(f"东方财富 {params.get('reportName')} 返回异常：{body.get('message')}")
        return body
