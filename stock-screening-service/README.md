# Stock Screening Service

A 股行情同步 + 高股息 MA120 筛股写库作业。正式链路由若依 Quartz 通过 `ProcessBuilder` 调用本目录 CLI；**不需要**常驻 `uvicorn :18081`。

FastAPI（`main.py`）仅保留本地调试，非正式依赖。

## 环境变量

- `TUSHARE_TOKEN`: 可选，Tushare Pro 授权码；未设置时使用仓库内默认值（可用环境变量覆盖）
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
export TUSHARE_TOKEN=<your_token>
export STOCK_DB_HOST=<mysql-host>
export STOCK_DB_USER=<user>
export STOCK_DB_PASSWORD=<password>
export STOCK_DB_NAME=appdb
python -m jobs.daily_run
# 可选参数：
#   --trade-date 20260722
#   --lookback-days 125
#   --skip-sync          # 仅筛股写结果，跳过 Tushare 同步
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
