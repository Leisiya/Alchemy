# 插件集成（通用若依）

> 类型：**通用若依**  
> 来源：<https://doc.ruoyi.vip/ruoyi-vue/document/cjjc.html>  
> 项目扩展列表：<https://doc.ruoyi.vip/ruoyi-vue/document/xmkz.html>（社区项目索引，非核心框架）

官方提供「下载 zip 覆盖工程」类集成方案。Agent **默认不要**为了炫技引入插件；仅当需求明确且本仓库未内置时再评估。

## 插件清单（官方章节）

| 主题 | 说明 |
| --- | --- |
| AI 模型对话 | 改 yml、Security 支持 ASYNC、覆盖模块代码 |
| Docker 一键部署 | 容器化 |
| PostgreSQL | 换库与方言 |
| 升级 Spring Boot 3.x | Security6 配置方式等（Alchemy 已是 Boot 4，勿按「升到 3」文档回退） |
| Ehcache / Ehcache3 | 本地缓存替代 Redis |
| WebSocket | 实时通信 |
| Electron | 桌面壳 |
| Atomikos | 分布式事务 |
| MinIO | 对象存储 |
| Easy-ES | 全文检索 |
| localStorage 代 cookie | Token 存储策略 |
| Undertow 替 Tomcat | Web 容器 |
| Actuator 优雅关闭 | 运维 |
| AJ-Captcha 滑块验证码 | 前后端一起改 |
| Sharding-JDBC | 分库分表 |
| JustAuth | 第三方登录 |
| 页面水印 | 前端 |
| MyBatis-Plus | 替换 MyBatis 配置（删原 MyBatisConfig） |
| EasyExcel | Excel 增强 |
| Knife4j | Swagger UI 增强 |
| Redisson | 分布式锁 |
| ip2region | 离线 IP |
| JSEncrypt | 密码加密传输 |
| HttpClient 增强 | HTTP 调用 |
| Druid 密码加密 | 数据源密码加密 |
| Browscap | UA 解析 |
| dynamic-datasource | 多数据源增强 |

## Agent 决策规则

1. **先查仓库是否已有能力**（Redis、Druid、Quartz 已内置）。  
2. **筛股业务**优先扩展 `stock-screening-service` + `ruoyi-system` 的 stock 包，而不是引入无关插件。  
3. 集成通常需要：改 `pom.xml`、改 `application.yml`、改 `SecurityConfig`、覆盖官方 zip——变更面大，需单独评审。  
4. 详细步骤以官方页面为准；本文件只作目录与风险提示。  
5. 「项目扩展」页是社区仓库列表，不是本仓库依赖。

## 与 Alchemy 的关系

| 能力 | Alchemy 现状（摘要） |
| --- | --- |
| Redis | 官方默认依赖，保留 |
| 筛股 HTTP 客户端 | 自研调用 `stock-screening-service`，非上述插件 |
| Vue3 / Boot2 | **不**迁移；保持 Vue2 + Boot4 |
