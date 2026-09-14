# 前端手册要点（通用若依）

> 类型：**通用若依**  
> 来源：<https://doc.ruoyi.vip/ruoyi-vue/document/qdsc.html>  
> 筛股产品页优先手工实现：[`../alchemy/conventions.md`](../alchemy/conventions.md)

## 全局插件方法

定义在 `src/plugins/`，经 `main.js` 挂到 Vue 原型。

### `$tab`（页签）

```js
this.$tab.openPage('用户管理', '/system/user')
this.$tab.updatePage(Object.assign({}, this.$route, { title: '自定义标题' }))
this.$tab.closePage()                    // 关当前回首页
this.$tab.closeOpenPage({ path: '/system/user' })
this.$tab.refreshPage()
this.$tab.closeAllPage()
this.$tab.closeLeftPage() / closeRightPage() / closeOtherPage()
```

### `$modal`

```js
this.$modal.msgSuccess('成功')
this.$modal.msgError('失败')
this.$modal.alert('提示')
this.$modal.notifyWarning('通知')
this.$modal.confirm('确认？').then(() => { /* ... */ }).catch(() => {})
this.$modal.loading('处理中...')
this.$modal.closeLoading()
```

### `$auth`

```js
this.$auth.hasPermi('system:user:add')
this.$auth.hasPermiOr(['system:user:add', 'system:user:edit'])
this.$auth.hasPermiAnd([...])
this.$auth.hasRole('admin')
this.$auth.hasRoleOr(['admin', 'common'])
```

模板指令更常用：`v-hasPermi="['system:user:add']"`、`v-hasRole`。

### `$cache` / `$download`

- `$cache.session` / `$cache.local`：封装 sessionStorage/localStorage  
- `$download`：文件下载（含 name/zip 等官方封装）

## 开发规范

| 类型 | 位置 |
| --- | --- |
| 页面 | `src/views/<模块>/...`，一路由一文件；模块内私有组件放同目录 `components/` |
| API | `src/api/<模块>/xxx.js`，按领域拆分 |
| 全局组件 | `src/components/` |
| 业务私有组件 | `views/.../components/` |
| 全局样式 | `assets/styles`；局部用 scoped |

## 请求流程

1. 页面调用 `api/xxx.js` 方法  
2. `utils/request.js`（axios）：统一 baseURL=`VUE_APP_BASE_API`、请求头 Token、错误码处理、超时  
3. 开发环境经 `vue.config.js` 代理到后端 `8080`，去掉 `/dev-api` 前缀  

示例：

```js
import request from '@/utils/request'
export function listUser(query) {
  return request({ url: '/system/user/list', method: 'get', params: query })
}
```

Token：`Authorization: Bearer ` + `getToken()`（`utils/auth.js`）。

## 路由

- **动态路由**：登录后根据后端菜单生成（`permission.js` + store）  
- **静态路由**：`router/index.js`（登录、404、隐藏详情页等）  
- 隐藏子页示例：`hidden: true` + `permissions` + `meta.activeMenu`

菜单配置字段（管理端）决定组件路径，如 `system/user/index` → `@/views/system/user/index`。

## 权限使用（前端）

- 按钮：`v-hasPermi` / `v-hasRole`  
- 逻辑：`$auth.*`  
- 路由：后端菜单 + 静态 `permissions`  

## 多级目录 / 页签缓存

- 多级菜单：后端菜单树；布局 `ParentView`/`Layout`  
- 缓存：路由 `meta.noCache`；需缓存的组件设置 `name` 与路由 `name` 一致  

## 图标 / 字典 / 参数

- 图标：SVG 放入 `src/icons/svg`，使用 `<svg-icon icon-class="password" />`；菜单图标自动扫描  
- 字典：`this.getDicts('sys_user_sex')` 或组件 `DictTag` / `dict-tag`  
- 参数：`getConfigKey('sys.index.skinName')` 等  

## 异常与路径

- 401：跳登录；业务码由 `request.js` 拦截  
- `publicPath` / 子路径部署：改 `vue.config.js` 的 `publicPath`，生产 Nginx 同步  
- 环境变量改完必须重启 dev server  

## Agent 改前端清单

1. 加 `api` → 加/改 `views` → 菜单组件路径对齐  
2. 权限字符与后端 `@PreAuthorize`、菜单按钮权限一致  
3. 列表页复用分页、RightToolbar、字典组件  
4. 产品向页面（筛股仪表等）按 Alchemy 约定手工实现
