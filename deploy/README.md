# Alchemy 生产部署

本目录是可拷贝到服务器的配置模板。应用、MySQL、Redis 通常部署在同一台 Ubuntu 主机上。  
生产进程通过 `alchemy.env` 连 **`127.0.0.1`**；本机 `./start-dev.sh` 仍走 `application*.yml`。不要在本机用这里的 systemd。

## 前置条件

发布脚本要求设置 **`DEPLOY_HOST`**（例如 `root@<host>` 或 `deploy@example.com`）：

```bash
export DEPLOY_HOST=root@<host>
```

本机需能免密 `ssh` 到该主机。可选 `DEPLOY_ROOT`（默认 `/opt/alchemy`）。

## 环境变量文件

1. 复制示例：`cp deploy/alchemy.env.example deploy/alchemy.env`（`alchemy.env` 已 gitignore，勿提交）。  
2. 在 `deploy/alchemy.env` 填入真实库密、Redis、`TUSHARE_TOKEN` 等。  
3. 首次上线或改密后，上传到服务器：`/opt/alchemy/conf/alchemy.env`。

## 日常更新（首次上线之后）

JDK / Nginx / Miniconda / `.venv` **不用再传**。在仓库根目录：

```bash
export DEPLOY_HOST=root@<host>
./deploy/release.sh
```

会本机打包 → 同步 jar、前端 `dist`、筛股源码 → 重启 `alchemy`。  
本次发布不会执行 MySQL DDL；已有生产库按需执行 `sql/patch_*.sql`（含 `patch_drop_code_gen.sql`），不要重跑完整的 `ry_20260417.sql`。

| 命令 | 作用 |
| --- | --- |
| `./deploy/release.sh` | 全量更新并重启后端 |
| `./deploy/release.sh backend` | 只发 jar 并重启 |
| `./deploy/release.sh frontend` | 只发前端（不用重启 Java） |
| `./deploy/release.sh python` | 只发筛股源码（不覆盖服务器 `.venv`） |
| `SKIP_BUILD=1 ./deploy/release.sh` | 不重新编译，只同步已有产物 |
| `./deploy/release.sh --deps` | 改了 `requirements.txt` 时，额外在服务器 pip 安装 |

## 目录约定

```text
/opt/alchemy/
  app/ruoyi-admin.jar
  ui/                          # 前端 dist 内容
  stock-screening-service/     # 含 .venv
  upload/                      # RUOYI_PROFILE
  logs/
  conf/alchemy.env             # 从本机 deploy/alchemy.env 拷贝（勿提交仓库）
```

## 关键约定

| 项 | 说明 |
| --- | --- |
| Java MySQL | `ruoyi-admin/.../application-druid.yml`（生产由 `alchemy.env` 覆盖） |
| Java Redis | `ruoyi-admin/.../application.yml` → `spring.data.redis` |
| Python 筛股库 | **必须**设 `STOCK_DB_*`，与 Java 同一库；CLI **不会**读 druid yml |
| Python 路径 | `STOCK_PYTHON` / `STOCK_SCREENING_DIR` 用绝对路径 |
| 上传目录 | `RUOYI_PROFILE`（默认 `/opt/alchemy/upload`） |
| 前端 API | `VUE_APP_BASE_API=/prod-api`，Nginx 须 `location ^~ /prod-api/`（`^~` 避免 js/css 正则抢走 Druid 资源） |
| 生产域名 | 在 Nginx 与 DNS 中配置 `https://example.com`（或你的子域）；IP 直连可选 `http://<host>` |

## 操作步骤

### 1. 依赖（新机首次）

在目标服务器上（或通过 `DEPLOY_HOST` 远程执行）：

```bash
export DEPLOY_HOST=root@<host>
./deploy/bootstrap-ubuntu.sh
./deploy/release.sh
./deploy/apply-nginx.sh
```

日常不要重装已有 MySQL/Redis。HTTPS 可用 Cloudflare 代理、Origin CA 或自签源站证书；若域名已走 CDN 代理，**不要**对已代理域名跑 `certbot --nginx`。

### 2. 建目录并拷配置

```bash
sudo mkdir -p /opt/alchemy/{app,ui,upload,logs,conf}
sudo cp deploy/alchemy.env /opt/alchemy/conf/alchemy.env   # 本地已填好真实值
```

### 3. 发布后端

```bash
mvn -DskipTests package
sudo cp ruoyi-admin/target/ruoyi-admin.jar /opt/alchemy/app/
```

或使用 `./deploy/release.sh backend`（需 `DEPLOY_HOST`）。

### 4. 发布前端

```bash
cd ruoyi-ui
npm install --registry=https://registry.npmmirror.com
npm run build:prod
sudo rsync -a --delete dist/ /opt/alchemy/ui/
```

或使用 `./deploy/release.sh frontend`。

### 5. Python 筛股

```bash
sudo rsync -a stock-screening-service/ /opt/alchemy/stock-screening-service/
cd /opt/alchemy/stock-screening-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

确认 `/opt/alchemy/conf/alchemy.env` 里 `STOCK_PYTHON`、`STOCK_SCREENING_DIR`、`STOCK_DB_*` 正确。

### 6. systemd

```bash
sudo cp deploy/alchemy.service /etc/systemd/system/alchemy.service
sudo systemctl daemon-reload
sudo systemctl enable --now alchemy
sudo systemctl status alchemy
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080
```

### 7. Nginx

站点写在 `/etc/nginx/conf.d/`（Ubuntu 会自动加载；脚本会关掉 `sites-enabled/default`）。在开发机：

```bash
export DEPLOY_HOST=root@<host>
./deploy/apply-nginx.sh
```

会同步 HTTP/HTTPS 配置、补齐自签源站证书，并 `nginx -s reload`。  
安全组开放 **80、443** 和 SSH；8080、3306、6379 不对公网开放。

### 8. 域名与 TLS（示例）

以 `example.com` 为例（替换为你的域名与 `<host>` IP）：

1. DNS：添加 `A` 记录指向 `<host>`；若用 Cloudflare，可开启代理（橙色云）。  
2. SSL：源站用自签或 Origin CA；CDN 与源站之间建议 **Full** 或 **Full (strict)**，避免 Flexible 混用导致异常。  
3. 边缘证书：开启 **Always Use HTTPS**；CDN 速度优化里 **不要**开 Rocket Loader（会打坏 Vue 后台）。  
4. 缓存（可选）：`example.com/prod-api/*` → Cache Level Bypass。

### 9. Google Analytics（可选）

1. GA4 为你的站点 URL 建 Web 数据流，复制衡量 ID（`G-` 开头）。  
2. 写入 `ruoyi-ui/.env.production` 的 `VUE_APP_GA_MEASUREMENT_ID`。  
3. `./deploy/release.sh frontend` 重新发前端。

### 10. 验收

1. `https://example.com`（或你的域名）打开登录页；`http://<host>` 可选直连  
2. 接口走 `/prod-api` 正常；上传写入 `/opt/alchemy/upload`  
3. 触发筛股（页面刷新或 Quartz），确认 CLI 成功且结果写入 `stock_screen_run` / `stock_screen_result`

## 文件一览

| 文件 | 用途 |
| --- | --- |
| `alchemy.env.example` | 环境变量模板（提交到 git） |
| `alchemy.env` | 本地真实配置（gitignore，勿提交） |
| `alchemy.service` | 后端常驻 |
| `nginx-alchemy.conf` | HTTP：`<host>` + 域名占位 |
| `nginx-alchemy-ssl.conf` | HTTPS 443 |
| `nginx-locations.conf` | 静态站 + `/prod-api` 反代 |
| `nginx-cloudflare-realip.conf` | 还原 CDN 客户端 IP（可选） |
| `apply-nginx.sh` | 同步 Nginx 并 reload |
| `README.md` | 本说明 |
| `bootstrap-ubuntu.sh` | Ubuntu 首次：目录、MySQL/Redis、空库导表 |
| `release.sh` | 日常一键发布（需 `DEPLOY_HOST`） |
