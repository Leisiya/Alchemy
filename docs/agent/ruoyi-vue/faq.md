# 常见问题（Agent 高频）（通用若依）

> 类型：**通用若依**  
> 来源：<https://doc.ruoyi.vip/ruoyi-vue/other/faq.html>  
> 完整条目很多；此处只保留 Agent 排障常用项。细节回官方页锚点。

## 认证与权限

### 不登录访问接口

- `SecurityConfig`：`permitAll()`（完全放行）或 `anonymous()`（有 Token 反而异常）  
- 或 `@Anonymous` 标在类/方法上，并去掉 `@PreAuthorize`  
- 前端页面：`permission.js` → `whiteList`

### 提示没有数据权限

角色数据范围 / `@DataScope` / 部门未分配；检查角色「数据权限」与用户部门。

### 业务模块 404

- Controller 的 `@RequestMapping` 与前端 api url 不一致  
- 新模块未加入 Maven 依赖或未扫描到 Mapper  
- 菜单组件路径错误导致前端路由 404（与后端 404 区分）

## 前端联调

### 更换后端地址

1. 开发：改 `ruoyi-ui/vue.config.js` 的 `baseUrl`（默认 `http://localhost:8080`）  
2. 改 `.env.*` 的 `VUE_APP_BASE_API`（如 `/dev-api`、`/prod-api`）  
3. 生产：Nginx `location ^~ /prod-api/` 反代到后端（必须 `^~`，见下条 Druid 静态资源 404）  

### 图片上传成功但不显示

- `ruoyi.profile` 路径与资源映射不一致  
- 域名/反向代理未转发 profile 资源  
- Token 或权限导致二次请求失败  

### 富文本上传/显示

自定义上传地址、HTML 展示、图片拖拽等见官方 FAQ 对应节。

## 菜单与路由

- **动态菜单**：以系统「菜单管理」为准；隐藏详情页可在 `router/index.js` 配静态 hidden 路由  
- **横向菜单 / TopNav**：布局设置或 `settings.js` 的 `topNav`  
- **页签标题**：`$tab.updatePage`  
- **缓存子页**：组件 `name` 对齐；`meta.noCache`  

## 构建与环境

| 问题 | 方向 |
| --- | --- |
| node-sass 安装失败 | 换 Node 版本、用 npmmirror、或按官方 FAQ 替换实现 |
| Node 版本过高 | 降到项目兼容 LTS |
| 生产图标乱码 | 构建/字体与 svg sprite 问题，查官方「生产环境图标」 |
| 分析包体积 | webpack-bundle-analyzer 等（官方有节） |

## 数据库与运维

- **多数据源**：`application-druid.yml` slave + `@DataSource`  
- **多类型数据库**：改驱动与 PageHelper 方言  
- **Linux 验证码乱码**：缺字体；安装 fontconfig/中文字体  
- **定时任务不执行**：检查 quartz 表、任务状态、集群配置  
- **Long 精度丢失**：前端用字符串或精度库；后端可转 String 输出  
- **XSS 过滤误伤**：特殊字符被滤 → 调整 xss 排除或编码策略  

## 安全相关（勿写死密钥）

- 改超级管理员密码：系统用户管理或重置 SQL（勿把新密码写进仓库文档）  
- Druid 控制台账号：`application-druid.yml` 的 `login-username`/`login-password`  
- Druid「Sign in」没反应：先看 iframe 里 `/prod-api/druid/js/jquery.min.js` 是否 404。生产 Nginx 的 `/prod-api/` 必须写 `location ^~`，否则扩展名正则会抢走 Druid 的 js/css  
- Token `secret`：生产必须替换 `application.yml` 中的默认值  

## Agent 排障顺序建议

1. 前端 Network：状态码、是否带 `Authorization`、实际命中的 URL（是否少了前缀剥离）  
2. 后端日志：权限拒绝 vs 业务异常 vs SQL  
3. 对照菜单权限字符与 `@PreAuthorize` / `v-hasPermi`  
4. 仍不明 → 用 curl 或浏览器 Network 直连验证（带 Bearer Token）  
5. 查本页同类 FAQ → 官方全文
