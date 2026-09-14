# Agent 知识底座（索引）

面向 Cursor Agent 的可检索知识。官方通用若依在 `ruoyi-vue/`，本仓库差异在 `alchemy/`（含产品页视觉 `alchemy/design/`）。

**冲突时**以 `.cursor/rules/alchemy.mdc` + [`alchemy/conventions.md`](alchemy/conventions.md) 为准。官方全文以 [`ruoyi-vue/SOURCE.md`](ruoyi-vue/SOURCE.md) 的 URL 为准。

Cursor 的 `.cursor/rules/` 是注入开关（短政策 + 去读哪篇），**不会**把本目录正文塞进每轮对话。本 README 给人看；glob 没打中时再打开它。

---

## 怎么走

```text
alchemy.mdc（每轮：中文、测试、系统工具、筛股页手工）
  → 改筛股 / Python：stock.mdc → conventions；改 UI 再读 alchemy/design/
  → 改 sql / Mapper：storage.mdc → data-storage.md
  → 权限 / 分页 / 路由：ruoyi.mdc → ruoyi-vue 对应篇
  → 对不上：看下面的任务表
```

---

## 放哪里

| 内容 | 位置 |
| --- | --- |
| 官方若依通用做法 | `docs/agent/ruoyi-vue/`（`SOURCE.md` 留 URL） |
| 本仓工程事实（模块、端口、筛股链路） | [`alchemy/conventions.md`](alchemy/conventions.md) |
| 本仓表 / Redis | [`alchemy/data-storage.md`](alchemy/data-storage.md) |
| 本仓产品页视觉 | [`alchemy/design/`](alchemy/design/MASTER.md) |
| 短政策与「去读哪」 | `.cursor/rules/` |
| 生产发布步骤 | 仓库 [`deploy/README.md`](../../deploy/README.md) |
| 本地联调 | 根目录 `./start-dev.sh`（不要用 `deploy/` 里的 systemd 起本机） |

禁止：在 rule 里复制手册；把任务稿写进 `docs/agent` 冒充现行约定；密钥进 docs；再在仓库根新建一套 `design-system/`。

Superpowers 任务稿（`docs/superpowers/`）**不是**现行架构约定；公开快照可不含该目录。现行事实以 `alchemy/` 与代码为准。

---

## 按任务路由（先读哪篇）

| 任务类型 | 先读 | 再读 |
| --- | --- | --- |
| 本地启动 / 部署 / 端口连不上 | [`ruoyi-vue/deploy.md`](ruoyi-vue/deploy.md) | [`alchemy/conventions.md`](alchemy/conventions.md)（含本地 vs 生产）；生产步骤见 [`deploy/README.md`](../../deploy/README.md) |
| 新增标准 CRUD 后台页 | [`ruoyi-vue/backend.md`](ruoyi-vue/backend.md)（权限、分页） | [`ruoyi-vue/frontend.md`](ruoyi-vue/frontend.md)；手工或 AI 编写，不用代码生成 |
| 联调接口 / 查权限 / 看响应结构 | curl、浏览器 Network；需要时看 Druid | [`ruoyi-vue/backend.md`](ruoyi-vue/backend.md)、[`faq.md`](ruoyi-vue/faq.md) |
| 筛股产品页 / 仪表榜单 | [`alchemy/conventions.md`](alchemy/conventions.md) | 手工实现；勿默认代码生成 |
| 改产品页视觉 / 认证与筛股交互 | [`alchemy/design/MASTER.md`](alchemy/design/MASTER.md) | 登录看 [`pages/login.md`](alchemy/design/pages/login.md)，筛股看 [`pages/screener.md`](alchemy/design/pages/screener.md) |
| MySQL 表 / Redis Key 归属 | [`alchemy/data-storage.md`](alchemy/data-storage.md) | [`alchemy/conventions.md`](alchemy/conventions.md) |
| 前端页面、路由、权限指令、`$tab`/`$modal` | [`ruoyi-vue/frontend.md`](ruoyi-vue/frontend.md) | [`ruoyi-vue/components.md`](ruoyi-vue/components.md) |
| 上传/分页/字典/导入组件 | [`ruoyi-vue/components.md`](ruoyi-vue/components.md) | — |
| 集成 Redis 以外的第三方插件 | [`ruoyi-vue/plugins.md`](ruoyi-vue/plugins.md) | 先确认本仓库是否已需要 |
| 报错排查（401、404、验证码、图标） | [`ruoyi-vue/faq.md`](ruoyi-vue/faq.md) | [`alchemy/conventions.md`](alchemy/conventions.md) |
| 技术栈 / 模块地图总览 | [`ruoyi-vue/overview.md`](ruoyi-vue/overview.md) | [`alchemy/conventions.md`](alchemy/conventions.md) |

---

## 目录树

```text
docs/agent/
├── README.md                 # 本索引（地图）
├── ruoyi-vue/                # 通用若依（提炼自官方文档）
│   ├── overview.md
│   ├── deploy.md
│   ├── backend.md
│   ├── frontend.md
│   ├── components.md
│   ├── plugins.md
│   ├── faq.md
│   └── SOURCE.md
└── alchemy/                  # 本仓库现行事实
    ├── conventions.md
    ├── data-storage.md
    └── design/               # 产品页视觉（MASTER + pages）
```

---

## Agent 使用约定

1. **先区分「通用若依」与「本仓库」**：改筛股业务、产品页时以 `alchemy/` 为准；改若依底座能力时读 `ruoyi-vue/`。
2. **联调不走 Swagger**：用 curl、浏览器 Network，或系统监控里的 Druid。标准 CRUD 手工或 AI 编写，**不要**再走 `/tool/gen`（`ruoyi-generator` 已移除）。
3. **不要整本镜像官方站**：细节以官方 URL（见 `SOURCE.md`）为准。
4. **密钥**：文档只用占位符；勿把真实密码、token 写入 docs。
5. **版本锚点**：本仓库 RuoYi **3.9.2**，Spring Boot **4.x** + JDK **17**，前端 **Vue 2 + Element UI**（见 `alchemy/conventions.md`）。
6. **长期事实变了才改本目录**（新表、新端口、视觉规格）。不要把任务稿写进这里冒充现行约定。
