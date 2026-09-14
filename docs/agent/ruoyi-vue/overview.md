# RuoYi-Vue 概览（通用若依）

> 类型：**通用若依**  
> 来源：<https://doc.ruoyi.vip/ruoyi-vue/>、<https://doc.ruoyi.vip/ruoyi-vue/document/kslj.html>、<https://doc.ruoyi.vip/ruoyi-vue/document/xmjs.html>  
> 本仓库差异见 [`../alchemy/conventions.md`](../alchemy/conventions.md)

## 是什么

RuoYi-Vue：Spring Boot + Spring Security + JWT + MyBatis + Vue 的前后端分离后台。内置用户/角色/菜单/部门、数据权限、字典/参数、日志、定时任务、代码生成、系统接口（Swagger/SpringDoc）、表单构建等。

## 官方版本矩阵（了解即可）

后端分支：

| 分支 | 说明 |
| --- | --- |
| master | Spring Boot 4.x，JDK 17+ |
| springboot3 | Spring Boot 3.x，JDK 17+ |
| springboot2 | Spring Boot 2.x，JDK 8+ |

前端变体：RuoYi-Vue（Vue2+Element UI）、RuoYi-Vue3（Vue3+Element Plus）、RuoYi-Vue3-TypeScript。

**Alchemy 锚定**：后端接近 master（Boot 4 / JDK 17），前端为 **Vue 2 + Element UI**（经典 ruoyi-ui），不是 Vue3。

## 系统需求（官方）

- JDK ≥ 1.8（Boot 3/4 实际需 17+）
- MySQL ≥ 5.7
- Maven ≥ 3.0
- Node ≥ 12
- Redis ≥ 3

## 内置功能（Agent 常碰）

| 能力 | 菜单/路径线索 | Agent 注意 |
| --- | --- | --- |
| 系统接口 | 官方若依曾内置 Swagger/SpringDoc | **Alchemy 已移除**；联调用 curl / Network |
| 表单构建 | 官方若依曾内置表单构建 | **Alchemy 已移除** |
| 定时任务 | 监控 → 定时任务 | `ruoyi-quartz` |
| 字典/参数 | 系统管理 | 前端 `dict`/`getConfigKey` |
| 角色菜单权限 | 系统管理 → 角色/菜单 | `@PreAuthorize` + `v-hasPermi` |

## 仓库模块结构（通用）

### 后端（Maven 多模块）

```text
com.ruoyi
├── ruoyi-admin       // Web 入口、Controller
├── ruoyi-framework   // Security、数据源、拦截器
├── ruoyi-system      // 系统业务 Service/Mapper/Domain
├── ruoyi-common      // 注解、工具、通用模型
├── ruoyi-quartz      // 定时任务
```

启动类：`com.ruoyi.RuoYiApplication`（在 `ruoyi-admin`）。

### 前端（`ruoyi-ui`）

```text
src/
├── api/           // 按业务拆分的 axios 请求
├── assets/
├── components/    // 全局组件
├── directive/     // 权限等指令
├── layout/
├── plugins/       // $tab $modal $auth $cache $download
├── router/
├── store/
├── utils/         // request.js、auth.js 等
├── views/         // 页面
├── permission.js  // 路由守卫、白名单
└── settings.js    // 主题/布局开关
```

环境文件：`.env.development` / `.env.production` / `.env.staging`（变量须 `VUE_APP_` 前缀）。

## 核心配置文件

| 文件 | 用途 |
| --- | --- |
| `ruoyi-admin/.../application.yml` | 端口、Redis、token、MyBatis、XSS、上传路径 `ruoyi.profile` |
| `application-druid.yml` | 数据源账号密码、Druid 监控 |
| `ruoyi-ui/vue.config.js` | 开发端口、代理到后端 |
| `ruoyi-ui/.env.*` | `VUE_APP_BASE_API`、`VUE_APP_TITLE` |

## 默认访问（官方约定）

| 端 | 地址 | 说明 |
| --- | --- | --- |
| 后端 API | `http://localhost:8080` | 无前端静态页 |
| 前端 | `http://localhost:80` | `npm run dev` |
| 默认账号 | `admin` / `admin123` | 演示默认；生产务必改 |

开发时代理：前端 `VUE_APP_BASE_API`（常为 `/dev-api`）→ `vue.config.js` 代理到 `http://localhost:8080`，并去掉前缀。

## 技术栈关键词

- 后端：Spring Boot、Spring Security、JWT（`Authorization: Bearer <token>`）、MyBatis、PageHelper、Druid、Redis
- 前端：Vue 2、Vuex、Vue Router 3、Axios、Element UI、Vue CLI

## Agent 速查

1. 改接口 → `ruoyi-admin` Controller + `ruoyi-system` Service/Mapper；权限用 `@PreAuthorize`。
2. 改页面 → `ruoyi-ui/src/views` + `src/api`；按钮权限 `v-hasPermi`。
3. 菜单入库后由后端动态路由下发；隐藏详情页可在 `router/index.js` 配静态 hidden 路由。
4. 本仓库筛股模块不在「通用若依」内，见 `alchemy/conventions.md`。
