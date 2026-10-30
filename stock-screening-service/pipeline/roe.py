from typing import Optional

from db.repositories import fetch_fina_indicator, upsert_fina_indicator
from pipeline.common import safe_float

FINA_INDICATOR_FIELDS = "ts_code,ann_date,end_date,roe,update_flag"


def _eligible_fina_rows(rows, trade_date: str) -> list:
    return [
        row for row in rows or []
        if str(row.get("ann_date") or "") and str(row.get("ann_date")) <= trade_date
    ]


def _prefer_revised_fina_rows(rows, trade_date: str) -> list:
    """Keep announced rows, then one per (ts_code, end_date) preferring update_flag=1."""
    best: dict[tuple[str, str], dict] = {}
    for row in _eligible_fina_rows(rows, trade_date):
        key = (str(row.get("ts_code") or ""), str(row.get("end_date") or ""))
        flag = 1 if str(row.get("update_flag") or "") == "1" else 0
        prev = best.get(key)
        prev_flag = 1 if prev is not None and str(prev.get("update_flag") or "") == "1" else 0
        if prev is None or flag > prev_flag:
            best[key] = row
    return list(best.values())


def pick_latest_roe(rows, trade_date: str) -> Optional[float]:
    eligible = _eligible_fina_rows(rows, trade_date)
    if not eligible:
        return None
    best = max(
        eligible,
        key=lambda row: (
            str(row.get("end_date") or ""),
            1 if str(row.get("update_flag") or "") == "1" else 0,
        ),
    )
    return safe_float(best.get("roe"))


def attach_candidate_roe(conn, pro, ts_codes, trade_date: str) -> dict[str, Optional[float]]:
    result: dict[str, Optional[float]] = {code: None for code in ts_codes}
    if not ts_codes:
        return result

    cached_by_code: dict[str, list] = {}
    for row in fetch_fina_indicator(conn, ts_codes):
        cached_by_code.setdefault(row["ts_code"], []).append(row)

    for code in ts_codes:
        try:
            rows = cached_by_code.get(code, [])
            if _eligible_fina_rows(rows, trade_date):
                result[code] = pick_latest_roe(rows, trade_date)
                continue
            df = pro.fina_indicator(ts_code=code, fields=FINA_INDICATOR_FIELDS)
            fetched = df.to_dict("records") if df is not None and not df.empty else []
            fetched = _prefer_revised_fina_rows(fetched, trade_date)
            if fetched:
                upsert_fina_indicator(conn, fetched)
            result[code] = pick_latest_roe(fetched, trade_date)
        except Exception:
            result[code] = None
    return result
