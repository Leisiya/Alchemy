# Alchemy 仓库约定（相对官方若依）

> 类型：**本仓库约定**  
> 优先于通用若依文档中的默认示例。冲突时以 `.cursor/rules/alchemy.mdc` + 本文为准。  
> 通用知识：[`../README.md`](../README.md)

## 产品定位

- 核心是 **A 股筛股平台产品化**，不是通用后台能力堆叠。  
- 仪表页、榜单页、用户直接使用的数据产品页 → **优先手工实现**。  
- 标准后台管理、联调、辅助录入 → 可用若依系统工具。

## 技术锚点（以仓库为准）

| 项 | Alchemy 实际 |
| --- | --- |
| RuoYi 版本 | 3.9.2（`pom.xml` / `package.json`） |
| 后端 | Spring Boot **4.0.x**，JDK **17**，Jakarta 命名空间 |
| 前端 | **Vue 2** + Element UI + Vue CLI（`ruoyi-ui`），**不是** Vue3 |
| 应用名 | 后端 `ruoyi.name: Alchemy`；前端 `VUE_APP_TITLE=Alchemy` |
| SQL | `sql/ry_20260417.sql`、`sql/quartz.sql` |
| 额外服务 | `stock-screening-service/`（Python CLI 写库；FastAPI 仅本地调试） |

官方文档里 Spring Boot 2.x / Vue3 示例仅作对照，**不要**按错版本改本仓库。

## 模块地图

```text
Alchemy/
├── ruoyi-admin          # Web 入口；含 stock Controller、定时任务入口
├── ruoyi-framework      # Security 等
├── ruoyi-system         # 含 stock domain/service/mapper + Python CLI 调度
├── ruoyi-common
├── ruoyi-quartz
├── ruoyi-ui             # 管理端前端；views/stock、api/stock
├── stock-screening-service   # Python 同步/筛股写库作业（非若依模块）
├── deploy/              # 生产部署：nginx / systemd / alchemy.env.example / README
├── sql/
├── docs/agent/          # 本知识底座
└── .cursor/rules/       # Cursor 短政策与按文件指针
```

Maven 模块列表不含 Python；`stock-screening-service` 由若依 Quartz 通过 ProcessBuilder 短生命周期拉起。

## 端口与联调（本仓库）

| 服务 | 默认 | 说明 |
| --- | --- | --- |
| 后端 | `8080` | `application.yml` → `server.port` |
| 前端 | `80` | `vue.config.js`；代理 `/dev-api` → `http://localhost:8080` |
| 筛股写库作业 | CLI `python -m jobs.daily_run` | 由若依 Quartz `stockScreeningTask` ProcessBuilder 触发；**不依赖**常驻 `:18081` |
| API 前缀 | `/dev-api` 开发，`/prod-api` 生产 | `.env.*` |

默认登录（若依惯例，未改库前）：`admin` / `admin123`。

## 本地联调 vs 生产部署

| | 本地 | 生产 |
| --- | --- | --- |
| 启动 | 根目录 [`start-dev.sh`](../../../start-dev.sh)（仅联调） | [`deploy/`](../../../deploy/)：`alchemy.service` + Nginx，步骤见 [`deploy/README.md`](../../../deploy/README.md) |
| 前端 | `npm run dev`，`/dev-api` | `npm run build:prod`，静态资源 + `/prod-api` |
| 上传目录 | `RUOYI_PROFILE`（建议 `$PWD/.runtime/upload`） | 默认 `/opt/alchemy/upload`（`application.yml` → `ruoyi.profile`） |
| Python 库 | `STOCK_DB_*` **必须与 Java 同一 MySQL** | 同左；由服务器 `/opt/alchemy/conf/alchemy.env` 注入，CLI **不会**读 `application-druid.yml` |

生产服务器目录约定：`/opt/alchemy/{app,ui,stock-screening-service,upload,logs,conf}`。`STOCK_PYTHON` / `STOCK_SCREENING_DIR` 用绝对路径。

## 筛股业务路径（本仓库）

| 层 | 路径 |
| --- | --- |
| 访客登录 | `POST /login/guest`（`SysLoginController`）；共享用户 `guest`，自选对访客拒绝 |
| 自选 | `ruoyi-admin/.../controller/stock/StockWatchlistController.java` → `/stock/watchlist`；前端静态路由 `/stock/watchlist`，复用 `screener/index.vue` |
| Controller | `ruoyi-admin/.../controller/stock/StockScreenResultController.java` → `/stock/screener` |
| Service | `ruoyi-system/.../StockScreeningServiceImpl.java`（查询只读库；`refreshLatest` 调 CLI） |
| CLI Runner | `ruoyi-system/.../PythonScreeningJobRunner.java` |
| 配置 | `StockScreenerProperties`（`python-executable` / `working-directory` / `job-module` / `timeout-seconds`） |
| 定时任务 | `ruoyi-admin/.../task/StockScreeningTask.java` |
| 前端 | `ruoyi-ui/src/views/stock/screener/`、`ruoyi-ui/src/api/stock/screener.js` |
| 权限字符示例 | `stock:screener:list` / `export` / `query` 等 |

Python 作业要点（详见该目录 README）：

```bash
cd stock-screening-service
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export TUSHARE_TOKEN=<你的令牌>   # 勿写入仓库文档真实值
# 另需 STOCK_DB_* 指向与 Java 同一 MySQL（见 README）
python -m jobs.daily_run
# 可选：--trade-date 20260722  --skip-sync
```

原始行情/估值数据缓存在 `stock_basic` / `stock_trade_cal` / `stock_daily_basic` / `stock_daily_quote`（详见 [`data-storage.md`](data-storage.md)）；筛股策略只读本地缓存。结果由 CLI 写入 `stock_screen_run` / `stock_screen_result`；Java/页面只做条件查询。

## 系统工具（与 `.cursor/rules/alchemy.mdc` 一致）

Alchemy 已移除表单构建与 Swagger/SpringDoc；联调走 curl、浏览器 Network，或系统监控里的 Druid。

## 相对官方的差异清单

| 主题 | 官方默认叙事 | Alchemy |
| --- | --- | --- |
| 产品目标 | 通用快速开发平台 | 筛股数据产品 |
| 演示库名 | `ry-vue` | 以本地/环境实际库为准（现多为 `appdb`） |
| 上传目录 | `D:/ruoyi/uploadPath` 示例 | `${RUOYI_PROFILE:/opt/alchemy/upload}`；本地用环境变量覆盖 |
| 生产部署 | 官方手册 Nginx 片段 | 本仓库 [`deploy/`](../../../deploy/) |
| 业务包 | `system`/`monitor`/`tool` | 另有 `stock` |
| 插件集成 | 大量可选 zip | 默认不引入；优先自研筛股链路 |
| Boot/Vue 版本 | 文档混有 2.x 示例 | Boot 4 + Vue 2 |
| 产品 UI | 若依默认蓝 / 通用后台皮肤 | [`design/MASTER.md`](design/MASTER.md)；筛股页看 [`design/pages/screener.md`](design/pages/screener.md)，认证页看 [`design/pages/login.md`](design/pages/login.md) |

## 密钥与配置安全

- `docs/agent/` 正文：**只用占位符**，勿把真实密码、token 写进 Agent 文档。  
- 生产环境变量：真实文件 [`deploy/alchemy.env`](../../../deploy/alchemy.env) **不纳入 git**（见 `.gitignore`）；仓库只提交 [`deploy/alchemy.env.example`](../../../deploy/alchemy.env.example)。部署时拷贝为本地 `deploy/alchemy.env` 填真实值，再上传到服务器 `/opt/alchemy/conf/alchemy.env`。  
- 若在文档中描述连接方式，仍写：`jdbc:mysql://<host>:3306/<db>`、`username: <user>`、`password: <secret>`。

## Agent 工作流建议

1. 读 `.cursor/rules/alchemy.mdc` 与本文。  
2. 若依底座问题 → `docs/agent/ruoyi-vue/*`。  
3. 筛股功能 → 先查 `stock` 包与 `stock-screening-service`，再改。  
4. 联调 → curl / Network / Druid；验证权限字符与菜单。  
5. 不要为了「对齐官方插件文档」而升级到 Vue3 或降级 Boot。
