# Screener Page Overrides

> **PROJECT:** Alchemy
> Rules here **override** `docs/agent/alchemy/design/MASTER.md` for the stock screener workbench.

---

## Layout

- Full-width workbench inside the RuoYi shell. Light background `--color-background`.
- Card: padding 16–24px, radius `--radius-lg` (12px), shadow `--shadow-card`.
- Page `h1` (22px) sits in `.detail-heading` on the **left** of the title row, with an optional `p.detail-rule-hint` (12px muted caption, not an `h2`) immediately to its right:
  - 股票列表：`PE < 20 · 股息率 > 3% · 市值 > 50 亿`
  - 破位低估：`现价/MA120 < 0.88`
  - 强势突破：`现价/MA120 > 1.12`
  - 我的自选：no hint.
- `.detail-actions` on the **right** of the title row: `数据截至 8月29日收盘 · 2小时前同步` (`.detail-updated-at`, `role="status"`, 12px muted) followed by Export. Current year omits the year; other years use `2025年8月29日`. Refresh the label every 60s (`nowMs` only — do not auto-poll the screener API). No「快照 · N 只」subtitle; row count comes from pagination only.
- Filter toolbar is stacked rows (`.screener-toolbar`):
  - **Row 1:** three text filters with **prepend** labels (代码 / 名称 / 行业), then Search / Reset buttons aligned to the same height.
  - **Row 2:** five numeric **range** groups (PE, PB, ROE, 股息率, 市值), each showing「最低 — 最高」with the metric name in prepend. Do not add 现价 / MA120 / 现价/MA120 as filters (those stay table columns). Do not use `label-width="68px"` inline forms or `label-position="top"`.
- Export is a ghost/default button on the title row. Never Element `type="warning"`.
- Do **not** mount `RightToolbar` (search-toggle / refresh circles).
- Default table `pageSize` 20.
- Trade date is page meta only. Do not repeat it as a table column when the page queries the latest snapshot.

### Mobile (`device === mobile`，小于 992px)

- 根 class `screener-dashboard--mobile`。
- 筛选默认收起；一条「筛选」按钮（`aria-expanded`）；点开后仍是现有 prepend 两行表单；不要 `label-position="top"`。
- 筛选区紧凑左对齐：两行 `.screener-toolbar__row` 用 `display: contents` 摊平；范围组 `inline-flex`、`width: auto`；各 prepend 统一 `min-width`（按「股息率」三字），`box-sizing: border-box`。
- 搜索/重置排在**全部**条件字段之后（`.screener-toolbar__actions { order: 1 }`），同一行 `flex: 1` 等宽，可点区域 `min-height: 44px`。
- 表格外包横滑改由表体承担：星标+股票 `fixed="left"`；表头下滑钉住（`el-table` 高度吃满标题/筛选/分页之下的剩余视口）；不做卡片列表。
- 手机列一律绑定固定 `width`（`:width="isMobile ? … : …"`），防止 `fit` 拉宽；股票/行业桌面与手机都用 `width`，禁止仅靠 `min-width`（桌面股票 104、行业 80，见 Typography）。
- 首屏横滑前须可见：星标 + 股票 + 行业 + 至少一列数字（如 PE）。手机列宽：星标 44，股票 108，行业 72，PE/PB/现价/ROE 56，股息率 64，市值 72（表头「市值」），MA120 64，现价/MA120 80，信号 88。
- 星标可点区域 ≥44px。
- 标题行允许「更新于」换行；导出仍在标题区，`plain` 不是 `warning`。

## Color

- Use Master light tokens. Captions / footnotes: `--color-muted-foreground` `#475569` only.
- Signal tags keep **text** (破位低估 / 强势突破 / 有待观察); color is supplementary.
- Dividend yield uses a primary-tint `metric-badge` that still shows the numeric text. **ROE** is plain right-aligned text via `formatPercent` — no badge.

## Typography (table)

- Stock column: name 14px / 700, code 12px muted underneath. Name links use `$color-primary` (`#15803D`); plain-text names (unparseable `tsCode`) stay `$color-foreground`.
- Numeric columns: right-aligned, `font-variant-numeric: tabular-nums`, 13px. Two decimal places for PE / PB / price / MA / ratio; thousands separators for 市值; percent for ROE and 股息率.
- Text columns (股票 / 行业 / 信号) stay left-aligned; the star column is centered. Do not mix alignments within a column type.
- Headers: 12px, muted, medium weight, `white-space: nowrap`. Cell left/right padding 8px.
- Desktop column widths (labels unchanged): 星标 44, 股票 **width** 104, 行业 **width** 80, PE/PB min 68, ROE min 72, 股息率 min 84, 市值(亿元) min 112, 现价 min 68, MA120 min 80, 现价/MA120 min 112, 信号 108. Stock/industry must use `width`, not `min-width`, so leftover space goes to numeric columns. Target ~1000px so 1280 with sidebar open does not need horizontal scroll.
- Dividend `metric-badge` min-width 56px and 4px horizontal padding so it fits the 84px 股息率 column.
- Row height about 48px. No zebra striping; hover is a light gray wash.
- Column order after 行业: PE → PB → **ROE** → 股息率 → 市值(亿元) → 现价 → MA120 → 现价/MA120 → 信号.

## Charts

- Table is the primary view. **No** ECharts, streaming area, sparklines, or candlesticks on this page.

## Interaction

- Table-area heading (`.detail-title`) is the page `h1`. The pool/signal caption sits beside it in `p.detail-rule-hint` (not inside the `h1`, not an `h2`). Search / export buttons `size="small"`.
- Persist filters in `$route.query`: `tsCode`, `name`, `industry`, `pageNum`, plus each range min/max (`peTtmMin`/`peTtmMax`, `pbMin`/`pbMax`, `roeMin`/`roeMax`, `dvTtmMin`/`dvTtmMax`, `totalMvYiMin`/`totalMvYiMax`). Do not overwrite route `meta.signal`. Do not persist `closePrice*` / `ma120*` / `priceMa120Ratio*` query params.
- 用户覆盖页面默认排序时，在 `$route.query` 持久化可选的 `sortBy` / `sortOrder`（`asc`/`desc`）。永不持久化 `orderByColumn` / `isAsc`。
- 数值列 PE / PB / ROE / 股息率 / 市值 / 现价 / MA120 / 现价/MA120 使用 Element `sortable="custom"`（服务端排序）。星标、股票、行业、信号不可排序。不使用 `:default-sort`。
- PE、PB 首次点击升序；其他指标列首次点击降序。第三次点击或 Reset 恢复页面出厂默认（列表按股息率、破位低估按比值升序、强势突破按比值降序、自选按加入时间）。
- 不添加「序号」列。
- Inverted ranges (min > max) show `$modal.msgError('最低不能大于最高')` and block the query.
- Table `empty-text` when there are no rows; if no snapshot exists, explain that the scheduled job has not produced one yet.
- Table region `aria-busy="true"` while loading. Delay the spinner ~200ms.
- Export button `:loading` / `disabled` for the duration of `download()`.
- Explicit Search / Enter to query. Do not search on every keystroke.
- Keep three separate text filters (code / name / industry) with prepend labels inside the inputs.
- Leftmost column is a star toggle (`el-icon-star-on` / `el-icon-star-off`) using `--color-primary` when selected. Do not use Element `warning` gold.
- Watchlist route `/stock/watchlist` reuses this table. Hide export. Empty copy: `还没有自选股票，可在股票列表中点击星标加入。`
- 侧栏「我的自选」用 `star`，「强势突破」用 `guide`（与表格星标语义一致）。
- Guest (`isGuest`): keep the star column and 我的自选 route. Do not call watchlist APIs. Opening `/stock/watchlist` shows an in-page `GuestWatchlistLock` card inside the detail card (title「自选功能需要注册」, CTA「立即注册完整账号」)—not an `el-dialog` overlay, so the sidebar stays clickable. Clicking a star on a list page uses `$modal.msgWarning('自选功能需要注册')` without a modal. Do not show a 3-stock quota card.
- Signal column: rows with `outOfPool` show「已不在候选池」first (muted chip); numeric cells stay `—`. Empty MA120 signal shows gray「有待观察」(`signal-chip--muted`), not a dash.
- 股票名称在 `tsCode` 可解析为 `SH`/`SZ`/`BJ` 时链到 `https://xueqiu.com/S/{EX}{6位数字}`，`target="_blank"` + `rel="noopener noreferrer"`。名称链接默认主色 700、无下划线、`cursor: pointer`；`:visited` 保持主色。悬停/focus 用 `$color-primary-hover` 加 `text-underline-offset: 3px` 的下划线；`:focus-visible` 用 2px ring。代码行保持纯文本。解析失败则名称仍为前景色纯文本。不加外链图标。访客同样可点。
