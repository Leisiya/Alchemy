# 后台手册要点（通用若依）

> 类型：**通用若依**  
> 来源：<https://doc.ruoyi.vip/ruoyi-vue/document/htsc.html>  
> 本仓库产品约定见 [`../alchemy/conventions.md`](../alchemy/conventions.md)

## 分页

前端 `pagination` + 参数 `pageNum`/`pageSize`；后端 `BaseController.startPage()` + PageHelper，返回 `TableDataInfo`（`rows`/`total`）。

```javascript
queryParams: { pageNum: 1, pageSize: 10 }
// <pagination ... @pagination="getList" />
listUser(this.queryParams).then(res => {
  this.userList = res.rows
  this.total = res.total
})
```

```java
startPage();
List<SysUser> list = userService.selectUserList(user);
return getDataTable(list);
```

## 导入导出（`@Excel`）

实体字段加 `@Excel`；导出常用：

```java
@Log(title = "用户管理", businessType = BusinessType.EXPORT)
@PreAuthorize("@ss.hasPermi('system:user:export')")
@GetMapping("/export")
public AjaxResult export(SysUser user) {
    List<SysUser> list = userService.selectUserList(user);
    ExcelUtil<SysUser> util = new ExcelUtil<>(SysUser.class);
    return util.exportExcel(list, "用户数据");
}
```

前端：`this.download('system/user/export', { ...queryParams }, 'user_xxx.xlsx')`  
导入：`ExcelUtil.importExcel` + 可选 `updateSupport`；模板接口 `importTemplate`。

常用注解属性：`name`、`dateFormat`、`dictType`、`readConverterExp`、`type`（ALL/EXPORT/IMPORT）、`cellType`（含图片）、`targetAttr`（嵌套对象）。

## 上传下载

- 通用上传接口：`/common/upload`（具体以 CommonController 为准）
- 前端 `el-upload` 必须带 `Authorization: Bearer ` + token
- 文件落盘路径受 `ruoyi.profile` 控制；下载用框架封装或 `$download`

## 权限注解

```java
@PreAuthorize("@ss.hasPermi('system:user:list')")
@PreAuthorize("@ss.lacksPermi('system:user:list')")
@PreAuthorize("@ss.hasAnyPermi('system:user:add,system:user:edit')")

@PreAuthorize("@ss.hasRole('admin')")
@PreAuthorize("@ss.hasAnyRoles('user,admin')")
```

公开接口（免登录）：

1. `SecurityConfig` 中 `permitAll()` / `anonymous()`  
2. 或方法/类上 `@Anonymous`（同时去掉该接口的 `@PreAuthorize`）

前端免登录页：`src/permission.js` 的 `whiteList`。

## 数据权限 / 多数据源

- `@DataScope`：按部门等过滤 SQL（需 Mapper XML 配合）。
- `@DataSource`：切换主从；从库在 `application-druid.yml` 的 `slave.enabled`。

## 事务 / 校验 / 脱敏 / 日志

| 能力 | 用法 |
| --- | --- |
| 事务 | `@Transactional` |
| 参数校验 | `@Validated` + Bean Validation 注解 |
| 脱敏 | `@Sensitive` 等（返回序列化） |
| 操作日志 | `@Log(title=..., businessType=...)` |
| 防重复提交 | `@RepeatSubmit` |

异常：业务抛 `ServiceException` 等，由全局异常处理转成统一 `AjaxResult`。

## 代码生成

官方若依带 `/tool/gen`。**Alchemy 已移除** `ruoyi-generator` 模块、菜单和 `gen_table*` 表。标准 CRUD 用手写或 AI，不要再找代码生成页。存量库执行 `sql/patch_drop_code_gen.sql`。

## 定时任务

- 模块：`ruoyi-quartz`
- 管理端配置 cron；目标方法需符合若依任务调用约定（Bean.method）
- SQL：`sql/quartz.sql`

## 系统接口（已移除）

**Alchemy 已移除**：管理端菜单、相关依赖与前端页面均已删除。存量库执行 `sql/patch_drop_system_tools.sql`。

联调请直接调用已认证 API（curl 或浏览器 Network 带 `Authorization: Bearer <token>`），需要时查看系统监控里的 Druid。

## 防重复提交

后端 `@RepeatSubmit`；前端对按钮/请求做节流也可配合。

## 国际化

后台 `i18n/messages`；前端可扩展 `LangSelect`（官方流程较长，按需查原文档）。

## 新建子模块（概要）

1. 新建 Maven module，依赖 `ruoyi-common`/`ruoyi-system` 等。
2. 根 `pom.xml` 增加 `<module>`；`ruoyi-admin` 引入依赖。
3. 包扫描/Mapper 扫描覆盖新包（通常 `com.ruoyi.**` 已覆盖）。
4. 前端新增 `api/` + `views/`，菜单组件路径指向 `views` 下路径。

## Agent 实现清单（新后台 CRUD）

1. 表结构  
2. Controller：`@PreAuthorize` + `startPage` + `@Log`  
3. 菜单权限字符与注解一致（如 `stock:screener:list`）  
4. 前端 api + view + `v-hasPermi`  
5. curl / Network 验证 → 角色授权 → 联调
