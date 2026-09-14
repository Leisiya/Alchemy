# 环境部署（通用若依）

> 类型：**通用若依**（含本仓库端口/脚本对照）  
> 来源：<https://doc.ruoyi.vip/ruoyi-vue/document/hjbs.html>  
> Alchemy 差异：[`../alchemy/conventions.md`](../alchemy/conventions.md)（本地 vs 生产、`STOCK_DB_*`）  
> Alchemy 生产步骤：仓库根目录 [`deploy/README.md`](../../../deploy/README.md)

## 依赖准备

```text
JDK（Alchemy：17）
MySQL >= 5.7
Redis >= 3
Maven >= 3
Node >= 12（建议 LTS；过高可能踩 node-sass 坑，见 faq.md）
```

前端安装依赖时用 npm 官方或 npmmirror，**不建议 cnpm**：

```bash
cd ruoyi-ui
npm install --registry=https://registry.npmmirror.com
```

## 后端运行

1. 用 IDE 导入根 `pom.xml`（Maven 多模块），或命令行构建。
2. 建库并导入 SQL：官方示例库名 `ry-vue`；脚本在 `sql/`（如 `ry_YYYYMMDD.sql`、`quartz.sql`）。  
   **Alchemy**：见 `alchemy/conventions.md`（库名/脚本以仓库为准）。
3. 改数据源：`ruoyi-admin/src/main/resources/application-druid.yml`  
   - `spring.datasource.druid.master.url` / `username` / `password` → 使用本地或受控环境凭证，**勿把真实密码写入文档或提交到公开渠道**。
4. 启动：`com.ruoyi.RuoYiApplication`  
   - 或根目录 `./ry.sh` / `ry.bat`（若依脚本）  
   - 成功标志日志含「若依启动成功」。
5. 验证：`http://localhost:8080`（仅 API，无完整前端页）。

关键配置：

```yaml
# application.yml
server:
  port: 8080
ruoyi:
  profile: /path/to/uploadPath   # Mac/Linux 必须可写；Windows 示例 D:/ruoyi/uploadPath
spring:
  redis:
    host: localhost
    port: 6379
    password:                    # 无密码留空
```

## 前端运行

```bash
cd ruoyi-ui
npm install --registry=https://registry.npmmirror.com
npm run dev
```

- 默认开发端口：**80**（`vue.config.js`）
- 打开 `http://localhost:80`，默认账号 **`admin` / `admin123`**
- 代理：`VUE_APP_BASE_API`（开发多为 `/dev-api`）→ `http://localhost:8080`

前后端**都要启动**才能完整使用。

## 必要配置清单

| 项 | 文件 | 动作 |
| --- | --- | --- |
| 数据库 | `application-druid.yml` | URL/账号/密码 |
| HTTP 端口 | `application.yml` → `server.port` | 默认 8080 |
| 上传目录 | `application.yml` → `ruoyi.profile` | 保证进程可写 |
| Redis | `application.yml` | host/port/password |
| 前端 API 前缀 | `.env.development` 等 | `VUE_APP_BASE_API` |
| 后端代理目标 | `vue.config.js` → `baseUrl` | 默认 `http://localhost:8080` |

## 生产部署要点

### 后端

```bash
# 多模块：产物在 ruoyi-admin/target
# 可用 bin/package.bat 或 mvn package
java -jar ruoyi-admin/target/ruoyi-admin.jar
# 或脚本 bin/run.bat
```

War 部署：将 `ruoyi-admin` 的 `packaging` 改为 `war`，按需排除内嵌 Tomcat（官方手册有片段）。

### 前端

```bash
cd ruoyi-ui
npm run build:prod    # 输出 dist/
npm run build:stage   # staging
```

将 `dist/` 放到 Nginx/静态服务器。`history`/`hash` 与 `publicPath` 需与部署路径一致。

### Nginx 典型反代（官方示例精简）

```nginx
server {
    listen 80;
    server_name localhost;
    charset utf-8;

    location / {
        root   /path/to/ruoyi-ui/dist;
        try_files $uri $uri/ /index.html;
        index  index.html;
    }

    location ^~ /prod-api/ {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://localhost:8080/;
    }
}
```

生产环境前端 `VUE_APP_BASE_API` 常为 `/prod-api`，须与 Nginx `location` 一致。本仓库同时有 `location ~* \.(js|css|...)$` 缓存前端静态资源，`/prod-api/` 必须写成 `^~`，否则 Druid 控制台的 js/css 会被当成前端文件 404，登录按钮无响应。

## 环境变量（前端）

- 文件：`.env.development` / `.env.production` / `.env.staging`
- 必须以 `VUE_APP_` 开头
- 修改后需**重启** `npm run dev`

```js
console.log(process.env.VUE_APP_BASE_API)
```

## 部署常见坑（官方）

1. **Mac**：检查 `ruoyi.profile` 路径是否存在且可写。
2. **Linux 表名大小写**：`/etc/my.cnf` 可设 `lower_case_table_names=1` 后重启 MySQL。
3. **无权限写文件**：检查 `profile` 与 `logback.xml` 的 log 路径权限。
4. 仅启动后端看不到登录页 → 正常，需启动 `ruoyi-ui`。

更多见 [`faq.md`](faq.md)。
