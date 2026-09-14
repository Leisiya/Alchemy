# Alchemy

筛股数据产品，基于若依 [RuoYi-Vue 3.9.2](http://www.ruoyi.vip)（Spring Boot 4 / JDK 17 / Vue 2，Apache-2.0）。

## 本地启动

```bash
./start-dev.sh
```

依赖：**Java 17**、**Node.js**（前端 `ruoyi-ui`）、**MySQL**、**Redis**、Python 虚拟环境（`stock-screening-service/.venv`）。首次使用前请按项目文档初始化数据库（`sql/`）并安装前后端依赖。

## 环境变量

敏感配置通过环境变量或本地 yml 占位符提供，勿把真实密钥提交回仓库：

| 类别 | 变量 |
| --- | --- |
| JWT | `TOKEN_SECRET`（生产必须覆盖） |
| Tushare | `TUSHARE_TOKEN` |
| Python 筛股库 | `STOCK_DB_HOST`、`STOCK_DB_PORT`、`STOCK_DB_USER`、`STOCK_DB_PASSWORD`、`STOCK_DB_NAME` |
| Java MySQL | `SPRING_DATASOURCE_DRUID_MASTER_URL`、`SPRING_DATASOURCE_DRUID_MASTER_USERNAME`、`SPRING_DATASOURCE_DRUID_MASTER_PASSWORD` |
| Redis | `SPRING_DATA_REDIS_HOST`、`SPRING_DATA_REDIS_PORT`、`SPRING_DATA_REDIS_PASSWORD` |
| 邮件 | `SPRING_MAIL_USERNAME`、`SPRING_MAIL_PASSWORD`、`SPRING_MAIL_FROM` |

本地开发可参考 `deploy/alchemy.env.example` 与 `ruoyi-admin/src/main/resources/application*.yml`。

## 默认登录

演示账号（若依惯例）：`admin` / `admin123`

## 生产部署

1. 复制 `deploy/alchemy.env.example` 为 **未纳入 git** 的 `deploy/alchemy.env`，填入真实值。  
2. 设置 `DEPLOY_HOST`（例如 `root@<host>`），详见 [`deploy/README.md`](deploy/README.md)。

## 公开快照说明

本公开快照为当前代码的 orphan 导出，不含原私有仓 git 历史。

## 安全提示

若你曾把本仓库的旧密钥用于生产，必须轮换 Tushare token、邮箱授权码、MySQL/Redis 密码、JWT secret。不要把真实密钥提交回仓库。

## 许可证

本项目采用 [Apache License 2.0](LICENSE)。RuoYi-Vue 同样为 Apache-2.0。
