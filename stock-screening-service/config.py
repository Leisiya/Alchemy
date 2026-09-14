import os


def get_tushare_token() -> str:
    token = os.getenv("TUSHARE_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TUSHARE_TOKEN is not configured")
    return token


def get_db_config() -> dict:
    return {
        "host": os.getenv("STOCK_DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("STOCK_DB_PORT", "3306")),
        "user": os.getenv("STOCK_DB_USER", "root"),
        "password": os.getenv("STOCK_DB_PASSWORD", ""),
        "database": os.getenv("STOCK_DB_NAME", "appdb"),
    }
