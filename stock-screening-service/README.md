# Stock Screening Service

A 股行情同步 + 高股息 MA120 筛股写库作业。正式链路由若依 Quartz 通过 `ProcessBuilder` 调用本目录 CLI；**不需要**常驻 `uvicorn :18081`。

## 数据源与兜底

行情统一经过 `sources/market_data.py` 的 `MarketData`：接口名、返回列和单位都与 Tushare 一致，每次调用按顺序尝试多个数据源。

| 数据 | 依次尝试 |
| --- | --- |
| 交易日历 `trade_cal` | Tushare → 新浪（AKShare）→ BaoStock |
| 股票列表 `stock_basic` | Tushare → 东方财富数据中心 → BaoStock → 库里上一次的列表 |
| 当日估值 `daily_basic` | Tushare → 腾讯行情快照 → 东方财富数据中心（股息率由分红明细计算） |
| 全市场日线 `daily`（按日期） | Tushare → 腾讯快照（仅当天收盘后）→ 东方财富数据中心（仅收盘价） |
| 个股日线 `daily`（按代码） | Tushare → 腾讯 → 新浪 → BaoStock |
| ROE `fina_indicator` | Tushare → 东方财富业绩报表 → BaoStock |

Tushare 只在设置了 `TUSHARE_TOKEN` 时启用。兜底规则：

- 某个源报错或数据没通过校验（行数太少、日期不对、关键字段大面积为空），就换下一个源；网络抖动、限流会先重试。
- 同一接口连续失败 3 次的源，本次运行不再使用（熔断），避免拖到 Java 侧 30 分钟超时。
- 所有源都说“这天的数据还没出”时返回空，沿用原来“当日估值数据尚未落地”的等待逻辑，下个半点再试。
- 股票列表全部失败时沿用库里已有的列表；某些交易日的全市场日线拉不到时，只给候选股逐只补历史日线。
- 用了哪个源、哪个源失败，都写在日志里（Java 侧在 `backend.out.log`，带 `[screener]` 前缀）。

腾讯快照的股息率与东方财富按分红明细算出的股息率口径略有差异：2026-10-30 全市场比对，95% 的股票相差在 5% 以内。

FastAPI（`main.py`）仅保留本地调试，非正式依赖。

## 环境变量

- `TUSHARE_TOKEN`: 可选，Tushare Pro 授权码（`stock_basic` / `daily_basic` 需 2000 积分）。设置后优先用 Tushare，失败再走免费数据源；不设置只用免费数据源
- `STOCK_DB_HOST` / `STOCK_DB_PORT` / `STOCK_DB_USER` / `STOCK_DB_PASSWORD` / `STOCK_DB_NAME`: 可选，与 Java 同一 MySQL
- `STOCK_SCREENING_RETRY_TIMES` / `STOCK_SCREENING_RETRY_BASE_SLEEP_SECONDS`: 可选，同步重试参数

## 安装

```bash
cd stock-screening-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 正式入口（CLI）

```bash
export TUSHARE_TOKEN=<your_token>   # 可选
export STOCK_DB_HOST=<mysql-host>
export STOCK_DB_USER=<user>
export STOCK_DB_PASSWORD=<password>
export STOCK_DB_NAME=appdb
python -m jobs.daily_run
# 可选参数：
#   --trade-date 20260722
#   --lookback-days 125
#   --skip-sync          # 仅筛股写结果，跳过行情同步
```

筛股结果写入完整基本面候选池（PE < 20、股息率 > 3%、市值 > 50 亿），MA120 中间带和无 MA 的票 `ma120_signal` 为空。改策略后若只需重算、不拉数：

```bash
python -m jobs.daily_run --skip-sync
```

流程：sync（缓存表）→ screen（策略）→ persist（`stock_screen_run` / `stock_screen_result`）。成功 exit `0`，失败写失败 run 后 exit `1`。

若依侧配置见 `application.yml`：

```yaml
stock:
  screener:
    python-executable: .../stock-screening-service/.venv/bin/python
    working-directory: .../stock-screening-service
    job-module: jobs.daily_run
    timeout-seconds: 1800
```

## 本地调试（可选 FastAPI）

```bash
uvicorn main:app --host 127.0.0.1 --port 18081
```

- `GET /health`
- `POST /internal/sync/run`
- `POST /internal/screenings/high-dividend-ma120/run`（仅返回 JSON，不写结果表；写库请用 CLI）

## 首次回填

先建表：`mysql ... < sql/stock_market_cache.sql`

再跑：

```bash
python -m jobs.daily_run
```
