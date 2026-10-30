from jobs import daily_run


def test_main_success_calls_sync_screen_persist(monkeypatch):
    calls = []
    monkeypatch.setattr(daily_run, "get_connection", lambda: object())
    monkeypatch.setattr(daily_run, "build_market_data", lambda **_k: object())
    monkeypatch.setattr(daily_run, "run_sync", lambda *a, **k: calls.append("sync") or {"trade_date": "20260722"})
    monkeypatch.setattr(
        daily_run,
        "run_screen",
        lambda *a, **k: calls.append("screen")
        or {
            "strategy_code": "HIGH_DIVIDEND_MA120",
            "trade_date": "20260722",
            "run_started_at": "2026-07-22T10:00:00",
            "run_finished_at": "2026-07-22T10:01:00",
            "summary": {"total_count": 0, "low_count": 0, "high_count": 0},
            "results": [],
        },
    )
    monkeypatch.setattr(daily_run, "persist_success", lambda *a, **k: calls.append("persist") or 1)
    assert daily_run.main(["--trade-date", "20260722"]) == 0
    assert calls == ["sync", "screen", "persist"]


def test_main_failure_persists_failure_and_returns_1(monkeypatch):
    closed = {"done": False}

    class Conn:
        def close(self):
            closed["done"] = True

    monkeypatch.setattr(daily_run, "get_connection", lambda: Conn())
    monkeypatch.setattr(daily_run, "build_market_data", lambda **_k: object())
    monkeypatch.setattr(daily_run, "run_sync", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(daily_run, "persist_failure", lambda *a, **k: 2)
    assert daily_run.main(["--trade-date", "20260722"]) == 1
    assert closed["done"] is True


def test_main_persists_failure_when_valuations_missing(monkeypatch):
    persist = {"success": 0, "failure": 0}

    class Conn:
        def close(self):
            return None

    monkeypatch.setattr(daily_run, "get_connection", lambda: Conn())
    monkeypatch.setattr(daily_run, "build_market_data", lambda **_k: object())
    monkeypatch.setattr(
        daily_run,
        "run_sync",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("当日估值数据尚未落地")),
    )
    monkeypatch.setattr(daily_run, "persist_success", lambda *a, **k: persist.__setitem__("success", persist["success"] + 1))
    monkeypatch.setattr(daily_run, "persist_failure", lambda *a, **k: persist.__setitem__("failure", persist["failure"] + 1) or 2)

    assert daily_run.main(["--trade-date", "20260827"]) == 1
    assert persist["failure"] == 1
    assert persist["success"] == 0


def test_main_skips_when_resolved_trade_date_is_not_today(monkeypatch):
    calls = []
    monkeypatch.setattr(daily_run, "get_connection", lambda: object())
    monkeypatch.setattr(daily_run, "build_market_data", lambda **_k: object())
    monkeypatch.setattr(daily_run, "ensure_trade_date", lambda *_a, **_k: "20260828")
    monkeypatch.setattr(daily_run, "calendar_today", lambda: "20260831")
    monkeypatch.setattr(daily_run, "run_sync", lambda *a, **k: calls.append("sync"))
    monkeypatch.setattr(daily_run, "run_screen", lambda *a, **k: calls.append("screen"))
    monkeypatch.setattr(daily_run, "persist_success", lambda *a, **k: calls.append("persist"))
    monkeypatch.setattr(daily_run, "persist_failure", lambda *a, **k: calls.append("fail"))
    assert daily_run.main([]) == 0
    assert calls == []


def test_main_skips_when_success_run_already_exists(monkeypatch):
    calls = []
    monkeypatch.setattr(daily_run, "get_connection", lambda: object())
    monkeypatch.setattr(daily_run, "build_market_data", lambda **_k: object())
    monkeypatch.setattr(daily_run, "ensure_trade_date", lambda *_a, **_k: "20260831")
    monkeypatch.setattr(daily_run, "calendar_today", lambda: "20260831")
    monkeypatch.setattr(daily_run, "find_success_run", lambda *_a, **_k: 42)
    monkeypatch.setattr(daily_run, "run_sync", lambda *a, **k: calls.append("sync"))
    monkeypatch.setattr(daily_run, "run_screen", lambda *a, **k: calls.append("screen"))
    assert daily_run.main([]) == 0
    assert calls == []


def test_main_waits_when_valuations_missing_without_trade_date(monkeypatch):
    persist = {"success": 0, "failure": 0}
    monkeypatch.setattr(daily_run, "get_connection", lambda: type("C", (), {"close": lambda self: None})())
    monkeypatch.setattr(daily_run, "build_market_data", lambda **_k: object())
    monkeypatch.setattr(daily_run, "ensure_trade_date", lambda *_a, **_k: "20260831")
    monkeypatch.setattr(daily_run, "calendar_today", lambda: "20260831")
    monkeypatch.setattr(daily_run, "find_success_run", lambda *_a, **_k: None)
    monkeypatch.setattr(
        daily_run,
        "run_sync",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("当日估值数据尚未落地")),
    )
    monkeypatch.setattr(daily_run, "persist_success", lambda *a, **k: persist.__setitem__("success", persist["success"] + 1))
    monkeypatch.setattr(daily_run, "persist_failure", lambda *a, **k: persist.__setitem__("failure", persist["failure"] + 1) or 2)
    assert daily_run.main([]) == 0
    assert persist["failure"] == 0
    assert persist["success"] == 0
