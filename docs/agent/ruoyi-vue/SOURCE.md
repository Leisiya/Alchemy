# 官方文档来源映射（SOURCE）

抓取基准：<https://doc.ruoyi.vip/ruoyi-vue/>（RuoYi-Vue 前后端分离版）  
整理日期：2026-07-20  

本目录文档是面向 Agent 的**提炼**，不是全文镜像。需要逐步细节时打开对应官方 URL。

## 侧边栏目录树 → 本地文件

| 官方章节 | 官方 URL | 本地提炼 |
| --- | --- | --- |
| 介绍 | https://doc.ruoyi.vip/ruoyi-vue/ | overview.md |
| 快速了解 | https://doc.ruoyi.vip/ruoyi-vue/document/kslj.html | overview.md |
| 环境部署 | https://doc.ruoyi.vip/ruoyi-vue/document/hjbs.html | deploy.md |
| 项目介绍 | https://doc.ruoyi.vip/ruoyi-vue/document/xmjs.html | overview.md、deploy.md |
| 后台手册 | https://doc.ruoyi.vip/ruoyi-vue/document/htsc.html | backend.md |
| 前端手册 | https://doc.ruoyi.vip/ruoyi-vue/document/qdsc.html | frontend.md |
| 组件文档 | https://doc.ruoyi.vip/ruoyi-vue/document/zjwd.html | components.md |
| 插件集成 | https://doc.ruoyi.vip/ruoyi-vue/document/cjjc.html | plugins.md |
| 项目扩展 | https://doc.ruoyi.vip/ruoyi-vue/document/xmkz.html | plugins.md（索引说明） |
| 常见问题 | https://doc.ruoyi.vip/ruoyi-vue/other/faq.html | faq.md |
| 更新日志 | https://doc.ruoyi.vip/ruoyi-vue/document/gxrz.html | 未全文收录（版本以仓库 pom 为准） |
| 视频教程 | https://doc.ruoyi.vip/ruoyi-vue/document/spjc.html | 未收录（外链视频） |
| 捐赠 | https://doc.ruoyi.vip/ruoyi-vue/other/donate.html | 不收录 |

## 后台手册子章节覆盖

分页、导入导出、上传下载、权限注解、事务、异常、参数验证、数据脱敏、系统日志、数据权限、多数据源、代码生成、定时任务、系统接口、防重复提交、国际化、新建子模块 → 均在 `backend.md` 有要点；逐步示例以官方 `htsc.html` 为准。

## 前端手册子章节覆盖

`$tab`/`$modal`/`$auth`/`$cache`/`$download`、开发规范、请求流程、路由、组件、权限、多级目录、页签缓存、图标、字典、参数、异常、应用路径 → `frontend.md`。

## 组件文档子章节覆盖

Pagination、Editor、RightToolbar、ImageUpload/Preview、FileUpload、DictTag、树分割、Excel 导入、表单设计、任务表达式 → `components.md`。

## 插件集成

官方 20+ 集成专题 → `plugins.md` 目录 + 决策规则；逐步操作回 `cjjc.html`。

## 未深度覆盖 / 抓取说明

| 项 | 说明 |
| --- | --- |
| 更新日志全文 | 仅记录存在；Alchemy 以 `pom.xml` 的 3.9.2 为准 |
| 视频教程 | 外链媒体，无文本可提炼 |
| 捐赠页 | 与开发无关 |
| 项目扩展社区列表 | 仅说明性质；不维护第三方仓库镜像 |
| FAQ 全量 80+ 条 | 提炼高频；其余回官方 |
| 插件逐步粘贴代码 | 避免仓库膨胀与过期；给清单与风险 |

## 侧边栏链接探测结果

从首页解析到的文档路径（相对 `/ruoyi-vue`）：

```text
/document/kslj.html
/document/hjbs.html
/document/xmjs.html
/document/htsc.html
/document/qdsc.html
/document/zjwd.html
/document/cjjc.html
/document/xmkz.html
/document/gxrz.html
/document/spjc.html
/other/faq.html
/other/donate.html
```

以上页面在整理时均可 HTTP 访问。
