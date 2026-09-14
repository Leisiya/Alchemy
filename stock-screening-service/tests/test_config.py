import os
import pytest

from config import get_tushare_token, get_db_config


def test_get_tushare_token_returns_env_value(monkeypatch):
    monkeypatch.setenv("TUSHARE_TOKEN", "abc123")
    assert get_tushare_token() == "abc123"


def test_get_tushare_token_raises_when_env_unset(monkeypatch):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="TUSHARE_TOKEN"):
        get_tushare_token()


def test_get_tushare_token_raises_when_default_cleared(monkeypatch):
    monkeypatch.setenv("TUSHARE_TOKEN", "   ")
    with pytest.raises(RuntimeError, match="TUSHARE_TOKEN"):
        get_tushare_token()


def test_get_db_config_uses_defaults(monkeypatch):
    for key in ("STOCK_DB_HOST", "STOCK_DB_PORT", "STOCK_DB_USER", "STOCK_DB_PASSWORD", "STOCK_DB_NAME"):
        monkeypatch.delenv(key, raising=False)
    cfg = get_db_config()
    assert cfg == {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "appdb",
    }


def test_get_db_config_reads_env_overrides(monkeypatch):
    monkeypatch.setenv("STOCK_DB_HOST", "10.0.0.5")
    monkeypatch.setenv("STOCK_DB_PORT", "3307")
    monkeypatch.setenv("STOCK_DB_USER", "app")
    monkeypatch.setenv("STOCK_DB_PASSWORD", "secret")
    monkeypatch.setenv("STOCK_DB_NAME", "appdb_test")
    cfg = get_db_config()
    assert cfg == {
        "host": "10.0.0.5",
        "port": 3307,
        "user": "app",
        "password": "secret",
        "database": "appdb_test",
    }
