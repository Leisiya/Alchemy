"""Deprecated for production. Prefer: python -m jobs.daily_run

FastAPI endpoints remain for local debug only.
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from clients.tushare_client import get_pro
from db.connection import get_connection
from pipeline.common import LOOKBACK_DAYS
from pipeline.screen_run import run_screen
from pipeline.sync_run import run_sync
from strategies.high_dividend_ma120 import STRATEGY_CODE

app = FastAPI(title="Stock Screening Service", version="2.0.0")


class SyncRequest(BaseModel):
    trade_date: Optional[str] = Field(default=None, description="YYYYMMDD")
    lookback_days: int = Field(default=LOOKBACK_DAYS)


class ScreeningRequest(BaseModel):
    trade_date: Optional[str] = Field(default=None, description="YYYYMMDD")


class ScreeningSummary(BaseModel):
    total_count: int
    low_count: int
    high_count: int


class ScreeningResultItem(BaseModel):
    ts_code: str
    trade_date: str
    name: Optional[str] = None
    industry: Optional[str] = None
    pe_ttm: Optional[float] = None
    pb: Optional[float] = None
    roe: Optional[float] = None
    dv_ttm: Optional[float] = None
    total_mv_yi: Optional[float] = None
    close_price: Optional[float] = None
    ma120: Optional[float] = None
    price_ma120_ratio: Optional[float] = None
    ma120_signal: str


class ScreeningResponse(BaseModel):
    strategy_code: str
    trade_date: str
    run_started_at: str
    run_finished_at: str
    summary: ScreeningSummary
    results: list[ScreeningResultItem]


@app.get("/health")
def health():
    return {"status": "ok", "strategy_code": STRATEGY_CODE, "data_source": "tushare"}


@app.post("/internal/sync/run")
def sync_run_endpoint(payload: Optional[SyncRequest] = None):
    conn = get_connection()
    pro = get_pro()
    try:
        req = payload or SyncRequest()
        return run_sync(conn, pro, req.trade_date, req.lookback_days)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        conn.close()


@app.post("/internal/screenings/high-dividend-ma120/run", response_model=ScreeningResponse)
def run_screening(payload: Optional[ScreeningRequest] = None):
    conn = get_connection()
    try:
        pro = get_pro()
        trade_date = None if payload is None else payload.trade_date
        out = run_screen(conn, pro, trade_date)
        return ScreeningResponse(
            strategy_code=out["strategy_code"],
            trade_date=out["trade_date"],
            run_started_at=out["run_started_at"],
            run_finished_at=out["run_finished_at"],
            summary=ScreeningSummary(**out["summary"]),
            results=[ScreeningResultItem(**item) for item in out["results"]],
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        conn.close()
