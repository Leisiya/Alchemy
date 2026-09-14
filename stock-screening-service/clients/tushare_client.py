import os
import time

from config import get_tushare_token

REQUEST_RETRY_TIMES = int(os.getenv("STOCK_SCREENING_RETRY_TIMES", "4"))
REQUEST_RETRY_BASE_SLEEP_SECONDS = float(os.getenv("STOCK_SCREENING_RETRY_BASE_SLEEP_SECONDS", "1.5"))


def is_rate_limit_error(exc: Exception) -> bool:
    message = str(exc)
    return "429" in message or "请求过于频繁" in message or "too many requests" in message.lower()


def call_with_retry(func, *args, **kwargs):
    last_error = None
    for attempt in range(1, REQUEST_RETRY_TIMES + 1):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            last_error = exc
            if not is_rate_limit_error(exc) or attempt == REQUEST_RETRY_TIMES:
                raise
            time.sleep(REQUEST_RETRY_BASE_SLEEP_SECONDS * attempt)
    raise last_error


def get_pro():
    import tushare as ts

    ts.set_token(get_tushare_token())
    return ts.pro_api()
