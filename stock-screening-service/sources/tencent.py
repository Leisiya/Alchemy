"""Tencent quotes: qt.gtimg.cn real-time snapshot + ifzq daily klines. Free, no token.

The snapshot is a "~"-separated positional record. Field meanings were checked one by one
against BaoStock and Eastmoney on 2026-10-30:
  3 close  4 pre_close  5 open  30 timestamp  31 change  32 pct_chg  33 high  34 low
  36 vol(lots)  37 amount(10k CNY)  38 turnover%  39 PE TTM  44 float mv(100M CNY)
  45 total mv(100M CNY)  46 PB  49 volume ratio  53 static PE  64 TTM dividend yield%
"""
import time
from typing import Callable, Optional

import pandas as pd
import requests

from sources.common import (
    HTTP_TIMEOUT_SECONDS,
    USER_AGENT,
    DataNotReady,
    Unsupported,
    from_prefixed,
    now_cn,
    num,
    positive,
    scaled,
    to_iso,
    to_prefixed,
    today_cn,
    with_price_changes,
)

QUOTE_URL = "https://qt.gtimg.cn/q="
KLINE_URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
BATCH_SIZE = 400
MIN_FIELDS = 65
# STAR market after-hours fixed-price trading ends 15:30; take the snapshot after that
SNAPSHOT_READY_AT = (15, 35)
REQUEST_INTERVAL_SECONDS = 0.05


def parse_snapshot(text: str, trade_date: str) -> tuple[list[dict], list[dict]]:
    """Turn a qt.gtimg.cn response into (daily_basic rows, daily rows) for stocks that traded on trade_date."""
    basic_rows, quote_rows = [], []
    for record in text.split(";"):
        if "~" not in record or "=" not in record:
            continue
        key, _, payload = record.strip().partition("=")
        fields = payload.strip('"').split("~")
        if len(fields) < MIN_FIELDS:
            continue
        stamp, vol = fields[30], num(fields[36])
        # suspended stocks keep an old timestamp or zero volume; Tushare daily leaves them out too
        if stamp[:8] != trade_date or not vol:
            continue
        ts_code = from_prefixed(key.strip()[2:])
        close = num(fields[3])
        basic_rows.append({
            "ts_code": ts_code,
            "trade_date": trade_date,
            "close": close,
            "turnover_rate": num(fields[38]),
            "volume_ratio": num(fields[49]),
            "pe": positive(fields[53]),
            "pe_ttm": positive(fields[39]),
            "pb": num(fields[46]),
            "dv_ttm": num(fields[64]),
            "total_mv": scaled(fields[45], 10000),
            "circ_mv": scaled(fields[44], 10000),
        })
        quote_rows.append({
            "ts_code": ts_code,
            "trade_date": trade_date,
            "open": num(fields[5]),
            "high": num(fields[33]),
            "low": num(fields[34]),
            "close": close,
            "pre_close": num(fields[4]),
            "change": num(fields[31]),
            "pct_chg": num(fields[32]),
            "vol": vol,
            "amount": scaled(fields[37], 10),
        })
    return basic_rows, quote_rows


def parse_kline(payload: dict, prefixed: str, ts_code: str) -> list[dict]:
    data = (payload.get("data") or {}).get(prefixed) or {}
    rows = []
    for item in data.get("day") or []:
        rows.append({
            "ts_code": ts_code,
            "trade_date": str(item[0]).replace("-", ""),
            "open": num(item[1]),
            "close": num(item[2]),
            "high": num(item[3]),
            "low": num(item[4]),
            "vol": num(item[5]),
            "amount": None,
        })
    return with_price_changes(rows)


class TencentSource:
    name = "tencent"

    def __init__(self, universe: Optional[Callable[[], list]] = None, session=None):
        self._universe = universe
        self._session = session or requests.Session()
        self._snapshots: dict[str, tuple[list, list]] = {}

    def daily_basic(self, trade_date: str, **_kwargs) -> pd.DataFrame:
        return pd.DataFrame(self._snapshot(trade_date)[0])

    def daily(self, trade_date=None, ts_code=None, start_date=None, end_date=None, **_kwargs) -> pd.DataFrame:
        if ts_code:
            return pd.DataFrame(self._history(ts_code, start_date, end_date))
        return pd.DataFrame(self._snapshot(trade_date)[1])

    def _snapshot(self, trade_date: str) -> tuple[list, list]:
        if trade_date in self._snapshots:
            return self._snapshots[trade_date]
        if trade_date != today_cn():
            raise Unsupported("腾讯实时行情只有当天的数据")
        now = now_cn()
        if (now.hour, now.minute) < SNAPSHOT_READY_AT:
            raise DataNotReady("还没收盘，不取当天快照")
        codes = [to_prefixed(code) for code in (self._universe() if self._universe else [])]
        if not codes:
            raise RuntimeError("没有股票列表，无法批量取腾讯行情")
        basic_rows, quote_rows = [], []
        for start in range(0, len(codes), BATCH_SIZE):
            resp = self._session.get(
                QUOTE_URL + ",".join(codes[start:start + BATCH_SIZE]),
                headers={"User-Agent": USER_AGENT},
                timeout=HTTP_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            resp.encoding = "gbk"
            basic, quotes = parse_snapshot(resp.text, trade_date)
            basic_rows.extend(basic)
            quote_rows.extend(quotes)
            time.sleep(REQUEST_INTERVAL_SECONDS)
        self._snapshots[trade_date] = (basic_rows, quote_rows)
        return basic_rows, quote_rows

    def _history(self, ts_code: str, start_date: str, end_date: str) -> list[dict]:
        prefixed = to_prefixed(ts_code)
        resp = self._session.get(
            KLINE_URL,
            # trailing empty field = unadjusted prices, same as Tushare daily
            params={"param": f"{prefixed},day,{to_iso(start_date)},{to_iso(end_date)},640,"},
            headers={"User-Agent": USER_AGENT},
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("code") not in (0, "0"):
            raise RuntimeError(f"腾讯日线返回异常：{payload.get('msg')}")
        return parse_kline(payload, prefixed, ts_code)
