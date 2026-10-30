"""Sina via AKShare: trading calendar and per-stock daily klines. Free, no token.

AKShare is used here because both endpoints need JS-side decoding that AKShare maintains.
"""
import pandas as pd

from sources.common import Unsupported, calendar_frame, num, to_prefixed, with_price_changes


class SinaSource:
    name = "sina"

    def trade_cal(self, exchange="SSE", end_date=None, is_open="1", limit=None, start_date=None, **_kwargs):
        if str(is_open) != "1":
            raise Unsupported("新浪交易日历只有开市日")
        import akshare as ak

        df = ak.tool_trade_date_hist_sina()
        days = [pd.Timestamp(day).strftime("%Y%m%d") for day in df["trade_date"]]
        return calendar_frame(days, exchange, end_date, limit, start_date)

    def daily(self, ts_code=None, start_date=None, end_date=None, **_kwargs) -> pd.DataFrame:
        if not ts_code:
            raise Unsupported("新浪只能按股票取历史日线")
        import akshare as ak

        df = ak.stock_zh_a_daily(symbol=to_prefixed(ts_code), start_date=start_date, end_date=end_date, adjust="")
        rows = [
            {
                "ts_code": ts_code,
                "trade_date": pd.Timestamp(item["date"]).strftime("%Y%m%d"),
                "open": num(item["open"]),
                "high": num(item["high"]),
                "low": num(item["low"]),
                "close": num(item["close"]),
                # Sina reports shares and CNY; Tushare daily uses lots and thousand CNY
                "vol": None if num(item["volume"]) is None else num(item["volume"]) / 100,
                "amount": None if num(item["amount"]) is None else num(item["amount"]) / 1000,
            }
            for item in (df.to_dict("records") if df is not None else [])
        ]
        return pd.DataFrame(with_price_changes(rows))
