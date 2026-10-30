"""Tushare-style market data facade that falls back across free sources.

Each method returns the same DataFrame (columns and units) as the Tushare API of the same name,
so sync / pipeline code does not care which source served it. For every call:
  - a source that errors, or whose data fails validation, is logged and the next one is tried;
  - a source that returns nothing / raises DataNotReady counts as "not published yet";
  - if no source delivers: return an empty frame when any source said "not yet" (keeps the existing
    "当日估值数据尚未落地" wait-and-retry behaviour), otherwise raise AllSourcesFailed.
A source that fails CIRCUIT_BREAK_AFTER times in a row for a method is skipped for the rest of the
run, so a dead source cannot stall per-stock loops until the job times out.
"""
import logging
import os
import time
from typing import Callable, Optional

import pandas as pd
import requests

from clients.tushare_client import REQUEST_RETRY_BASE_SLEEP_SECONDS, REQUEST_RETRY_TIMES, is_rate_limit_error
from sources.common import DataNotReady, Unsupported, parse_day, today_cn

logger = logging.getLogger(__name__)

CIRCUIT_BREAK_AFTER = 3
MIN_MARKET_ROWS = 3000
MIN_FILLED_RATIO = 0.8
MAX_CALENDAR_LAG_DAYS = 20


class AllSourcesFailed(RuntimeError):
    def __init__(self, method: str, errors: list[tuple[str, str]]):
        self.method = method
        self.errors = errors
        detail = "；".join(f"{name}: {error}" for name, error in errors) or "没有可用的数据源"
        super().__init__(f"{method} 所有数据源均失败（{detail}）")


def _is_retryable(exc: Exception) -> bool:
    if is_rate_limit_error(exc):
        return True
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return True
    response = getattr(exc, "response", None)
    return isinstance(exc, requests.HTTPError) and response is not None and response.status_code >= 500


def _short(exc: Exception) -> str:
    return f"{type(exc).__name__}: {str(exc)[:200]}"


def _check_trade_cal(df: pd.DataFrame, kwargs: dict) -> Optional[str]:
    days = sorted(str(day) for day in df["cal_date"])
    end = kwargs.get("end_date") or today_cn()
    if days[-1] > end:
        return f"最新交易日 {days[-1]} 晚于 {end}"
    if (parse_day(end) - parse_day(days[-1])).days > MAX_CALENDAR_LAG_DAYS:
        return f"交易日历只到 {days[-1]}，太旧"
    limit = kwargs.get("limit")
    if limit and len(days) < int(limit):
        return f"只有 {len(days)} 个交易日，要 {limit} 个"
    return None


def _check_stock_basic(df: pd.DataFrame, _kwargs: dict) -> Optional[str]:
    if len(df) < MIN_MARKET_ROWS:
        return f"股票列表只有 {len(df)} 只"
    return None


def _check_market_day(df: pd.DataFrame, kwargs: dict, filled_column: str) -> Optional[str]:
    trade_date = kwargs.get("trade_date")
    if len(df) < MIN_MARKET_ROWS:
        return f"只有 {len(df)} 只股票的数据"
    if (df["trade_date"].astype(str) != trade_date).any():
        return f"混入了不是 {trade_date} 的数据"
    filled = df[filled_column].notna().mean()
    if filled < MIN_FILLED_RATIO:
        return f"{filled_column} 只有 {filled:.0%} 有值"
    return None


def _check_daily_basic(df: pd.DataFrame, kwargs: dict) -> Optional[str]:
    return _check_market_day(df, kwargs, "total_mv")


def _check_daily(df: pd.DataFrame, kwargs: dict) -> Optional[str]:
    if kwargs.get("ts_code"):
        days = df["trade_date"].astype(str)
        if (df["ts_code"] != kwargs["ts_code"]).any():
            return "返回了别的股票"
        if (days < str(kwargs.get("start_date") or "")).any() or (days > str(kwargs.get("end_date") or "99999999")).any():
            return "返回了日期范围以外的数据"
        return None
    return _check_market_day(df, kwargs, "close")


class TushareSource:
    """The paid source, used first when TUSHARE_TOKEN is set (stock_basic / daily_basic need 2000 points)."""

    name = "tushare"

    def __init__(self, pro):
        self._pro = pro

    def trade_cal(self, **kwargs):
        return self._pro.trade_cal(**kwargs)

    def stock_basic(self, **kwargs):
        return self._pro.stock_basic(**kwargs)

    def daily_basic(self, **kwargs):
        return self._pro.daily_basic(**kwargs)

    def daily(self, **kwargs):
        return self._pro.daily(**kwargs)

    def fina_indicator(self, **kwargs):
        return self._pro.fina_indicator(**kwargs)


class MarketData:
    def __init__(self, providers):
        self.providers = list(providers)
        self.used: dict[str, str] = {}
        self._consecutive_failures: dict[tuple[str, str], int] = {}

    def trade_cal(self, **kwargs) -> pd.DataFrame:
        return self._first("trade_cal", kwargs, _check_trade_cal)

    def stock_basic(self, **kwargs) -> pd.DataFrame:
        return self._first("stock_basic", kwargs, _check_stock_basic)

    def daily_basic(self, **kwargs) -> pd.DataFrame:
        return self._first("daily_basic", kwargs, _check_daily_basic)

    def daily(self, **kwargs) -> pd.DataFrame:
        return self._first("daily", kwargs, _check_daily)

    def fina_indicator(self, **kwargs) -> pd.DataFrame:
        return self._first("fina_indicator", kwargs)

    def close(self) -> None:
        for provider in self.providers:
            closer = getattr(provider, "close", None)
            if closer is not None:
                try:
                    closer()
                except Exception:
                    logger.warning("关闭数据源 %s 失败", provider.name, exc_info=True)

    def _first(self, method: str, kwargs: dict, validate: Optional[Callable] = None) -> pd.DataFrame:
        errors: list[tuple[str, str]] = []
        not_ready = False
        for provider in self.providers:
            func = getattr(provider, method, None)
            key = (provider.name, method)
            if func is None or self._consecutive_failures.get(key, 0) >= CIRCUIT_BREAK_AFTER:
                continue
            try:
                df = self._call_with_retry(func, kwargs)
                problem = None if df is None or df.empty or validate is None else validate(df, kwargs)
            except Unsupported:
                continue
            except DataNotReady as exc:
                not_ready = True
                errors.append((provider.name, f"数据未就绪：{exc}"))
                continue
            except Exception as exc:
                self._record_failure(key, errors, _short(exc))
                continue
            if df is None or df.empty:
                not_ready = True
                errors.append((provider.name, "返回空数据"))
                continue
            if problem:
                self._record_failure(key, errors, f"数据校验未通过：{problem}")
                continue
            self._consecutive_failures[key] = 0
            self.used[method] = provider.name
            if errors:
                logger.warning("%s %s 改用 %s（前面的源：%s）", method, kwargs, provider.name, errors)
            return df
        if not_ready:
            logger.info("%s %s 暂无数据：%s", method, kwargs, errors)
            return pd.DataFrame()
        raise AllSourcesFailed(method, errors)

    def _record_failure(self, key: tuple[str, str], errors: list, message: str) -> None:
        errors.append((key[0], message))
        self._consecutive_failures[key] = self._consecutive_failures.get(key, 0) + 1
        if self._consecutive_failures[key] == CIRCUIT_BREAK_AFTER:
            logger.warning("%s.%s 连续失败 %d 次，本次运行不再使用：%s", *key, CIRCUIT_BREAK_AFTER, message)

    @staticmethod
    def _call_with_retry(func: Callable, kwargs: dict):
        for attempt in range(1, REQUEST_RETRY_TIMES + 1):
            try:
                return func(**kwargs)
            except Exception as exc:
                if attempt == REQUEST_RETRY_TIMES or not _is_retryable(exc):
                    raise
                time.sleep(REQUEST_RETRY_BASE_SLEEP_SECONDS * attempt)


def build_market_data(universe: Optional[Callable[[], list]] = None) -> MarketData:
    """Tushare first when a token is configured, then the free sources.

    `universe` returns the ts_codes to snapshot; the Tencent quote API has no "all stocks" query.
    """
    from sources.baostock_api import BaostockSource
    from sources.eastmoney import EastmoneySource
    from sources.sina import SinaSource
    from sources.tencent import TencentSource

    providers = []
    if os.getenv("TUSHARE_TOKEN", "").strip():
        from clients.tushare_client import get_pro

        providers.append(TushareSource(get_pro()))
    providers += [TencentSource(universe), EastmoneySource(), SinaSource(), BaostockSource()]
    return MarketData(providers)
