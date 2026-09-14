'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const screenerPath = path.join(__dirname, '../src/views/stock/screener/index.vue')

test('screener does not mount RightToolbar or warning export', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')
  assert.equal(source.includes('right-toolbar'), false)
  assert.equal(source.includes('RightToolbar'), false)
  assert.equal(/el-button[\s\S]{0,120}type="warning"/.test(source), false)
  assert.equal(source.includes('label-position="top"'), false)
  assert.equal(source.includes('stock-cell__name'), true)
  assert.equal(source.includes('metric-badge'), true)
})

test('screener filter labels sit inside inputs as prepend', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')

  assert.match(source, /slot="prepend">\s*代码\s*</)
  assert.match(source, /slot="prepend">\s*名称\s*</)
  assert.match(source, /slot="prepend">\s*行业\s*</)
  assert.equal((source.match(/slot="prepend"/g) || []).length, 8)

  assert.equal(source.includes('label-position="top"'), false)
  assert.equal(source.includes('<el-form-item label="代码"'), false)
  assert.equal(source.includes('<el-form-item label="名称"'), false)
  assert.equal(source.includes('<el-form-item label="行业"'), false)

  assert.equal(source.includes('placeholder="请输入股票代码"'), false)
  assert.equal(source.includes('placeholder="请输入股票名称"'), false)
  assert.equal(source.includes('placeholder="请输入行业"'), false)

  assert.equal(source.includes('handleQuery'), true)
  assert.equal(source.includes('@keyup.enter'), true)
  assert.equal(source.includes('@input'), false)

  assert.equal(source.includes('queryParams.tsCode'), true)
  assert.equal(source.includes('queryParams.name'), true)
  assert.equal(source.includes('queryParams.industry'), true)
})

test('screener shows ROE percent column after PB without metric-badge', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')
  assert.equal(source.includes('label="ROE"'), true)
  assert.equal(source.includes('formatPercent(scope.row.roe)'), true)

  const roeColumnMatch = source.match(/<el-table-column label="ROE"[\s\S]*?<\/el-table-column>/)
  assert.ok(roeColumnMatch, 'ROE column template should exist')
  assert.equal(roeColumnMatch[0].includes('metric-badge'), false)

  const tableColumnLabels = [...source.matchAll(/<el-table-column label="([^"]+)"/g)].map(match => match[1])
  const pbIndex = tableColumnLabels.indexOf('PB')
  const roeIndex = tableColumnLabels.indexOf('ROE')
  const dividendIndex = tableColumnLabels.indexOf('股息率')
  assert.ok(pbIndex >= 0, 'PB column should exist')
  assert.ok(roeIndex > pbIndex, 'ROE column should follow PB')
  assert.ok(dividendIndex > roeIndex, '股息率 column should follow ROE')
  assert.equal(roeIndex, pbIndex + 1, 'ROE column should sit immediately after PB')
  assert.equal(dividendIndex, roeIndex + 1, '股息率 column should sit immediately after ROE')
})

test('screener shows 有待观察 for empty MA120 signals after watchlist chip', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')
  assert.equal(source.includes('有待观察'), true)
  assert.equal(source.includes('signal-empty">—'), false)
  assert.equal(source.includes('已不在候选池'), true)

  const signalColumnMatch = source.match(/<el-table-column label="信号"[\s\S]*?<\/el-table-column>/)
  assert.ok(signalColumnMatch, 'signal column template should exist')
  const signalColumn = signalColumnMatch[0]
  const outOfPoolIndex = signalColumn.indexOf('scope.row.outOfPool')
  const pendingIndex = signalColumn.indexOf('有待观察')
  assert.ok(outOfPoolIndex >= 0, 'outOfPool chip should stay first')
  assert.ok(pendingIndex > outOfPoolIndex, '有待观察 should be the default branch after outOfPool')
  assert.match(signalColumn, /v-else[\s\S]*signal-chip signal-chip--muted[\s\S]*有待观察/)
})

test('screener toolbar has numeric range filters on a second row', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')

  assert.equal(source.includes('peTtmMin'), true)
  assert.equal(source.includes('roeMin'), true)
  assert.equal(source.includes('totalMvYiMin'), true)
  assert.equal(source.includes('priceMa120RatioMax'), false)
  assert.equal(source.includes('closePriceMin'), false)
  assert.equal(source.includes('queryParams.ma120Min'), false)
  assert.equal(source.includes('hasInvertedRange'), true)
  assert.equal(source.includes('hasInvalidRange'), true)
  assert.equal(source.includes('最低不能大于最高'), true)
  assert.equal(source.includes('请输入有效数字'), true)
  assert.equal(source.includes('$modal.msgError'), true)
  assert.equal(source.includes('omitBlankRanges'), true)
  assert.equal(source.includes('pickRangeQuery'), true)

  const rejectRange = source.slice(source.indexOf('rejectInvertedRange() {'), source.indexOf('\n    setListLoading'))
  assert.match(rejectRange, /hasInvalidRange\(this\.queryParams\)/)
  assert.match(rejectRange, /请输入有效数字/)
  assert.match(rejectRange, /hasInvertedRange\(this\.queryParams\)/)
  assert.ok(
    rejectRange.indexOf('hasInvalidRange') < rejectRange.indexOf('hasInvertedRange'),
    'invalid input should be rejected before inverted-range check'
  )

  const getList = source.slice(source.indexOf('getList() {'), source.indexOf('\n    toggleWatchlist'))
  assert.match(getList, /rejectInvertedRange\(\)/)
  assert.ok(getList.indexOf('rejectInvertedRange') < getList.indexOf('omitBlankRanges'))

  const handleExport = source.slice(source.indexOf('handleExport() {'), source.indexOf('\n  }\n}'))
  assert.match(handleExport, /rejectInvertedRange\(\)/)
  assert.ok(handleExport.indexOf('rejectInvertedRange') < handleExport.indexOf('omitBlankRanges'))

  assert.match(source, /slot="prepend">\s*PE\s*</)
  assert.match(source, /slot="prepend">\s*股息率\s*</)
  assert.match(source, /slot="prepend">\s*市值\s*</)
  assert.equal(/slot="prepend">\s*现价\s*</.test(source), false)
  assert.equal(/slot="prepend">\s*MA120\s*</.test(source), false)
  assert.equal(/slot="prepend">\s*现价\/MA120\s*</.test(source), false)
  assert.equal(source.includes('screener-toolbar__ranges'), true)
  assert.equal(source.includes('el-date-picker'), false)
  assert.equal(source.includes('@input'), false)
})

test('screener shows snapshot freshness beside export without 更新于 prefix', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')
  assert.equal(source.includes('更新于'), false)
  assert.equal(source.includes('formatSnapshotFreshness'), true)
  assert.equal(source.includes('nowMs'), true)
  assert.equal(source.includes('freshnessTimer'), true)
  assert.match(source, /setInterval\([\s\S]*60000/)
  assert.match(source, /beforeDestroy[\s\S]*clearInterval\(this\.freshnessTimer\)/)
  assert.equal(source.includes('role="status"'), true)
  assert.equal(source.includes('aria-atomic="true"'), true)

  const headingMatch = source.match(/<div class="detail-heading">[\s\S]*?<\/div>/)
  assert.ok(headingMatch, 'detail-heading should exist')
  assert.equal(headingMatch[0].includes('v-if="snapshotMeta"'), false)
  assert.match(headingMatch[0], /<h1 class="detail-title">\{\{\s*pageTitle\s*\}\}<\/h1>/)
  assert.match(headingMatch[0], /<p\s+v-if="pageRuleHint"\s+class="detail-rule-hint">\{\{\s*pageRuleHint\s*\}\}<\/p>/)
  assert.equal(headingMatch[0].includes('<h2'), false)
  assert.equal(source.includes('PE < 20 · 股息率 > 3% · 市值 > 50 亿'), true)
  assert.equal(source.includes('现价/MA120 < 0.88'), true)
  assert.equal(source.includes('现价/MA120 > 1.12'), true)
  assert.match(source, /pageRuleHint\(\)\s*\{[\s\S]*isWatchlistPage[\s\S]*return ""/)

  const actionsMatch = source.match(/<div class="detail-actions">[\s\S]*?<\/div>/)
  assert.ok(actionsMatch, 'detail-actions should exist')
  assert.match(actionsMatch[0], /\{\{\s*updatedAtLabel\s*\}\}/)
  assert.equal(actionsMatch[0].includes('更新于'), false)
  const freshnessIndex = Math.max(
    actionsMatch[0].indexOf('updatedAtLabel'),
    actionsMatch[0].indexOf('数据截至')
  )
  const exportIndex = actionsMatch[0].indexOf('导出')
  assert.ok(freshnessIndex >= 0, 'freshness label should be inside detail-actions')
  assert.ok(exportIndex >= 0, '导出 should be inside detail-actions')
  assert.ok(freshnessIndex < exportIndex, 'freshness label should appear before 导出 in detail-actions')

  const timerBody = source.slice(source.indexOf('setInterval('), source.indexOf('60000'))
  assert.match(timerBody, /this\.nowMs\s*=\s*Date\.now\(\)/)
  assert.equal(timerBody.includes('getList'), false)
  assert.equal(timerBody.includes('getLatestScreenDashboard'), false)
})

test('screener numeric columns use custom server sort and persist sortBy', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')

  assert.equal(source.includes('sortable="custom"'), true)
  assert.equal(source.includes("@sort-change=\"handleSortChange\""), true)
  assert.equal(source.includes('ref="resultTable"'), true)
  assert.equal(source.includes('handleSortChange'), true)
  assert.equal(source.includes('clearSort'), true)
  assert.equal(source.includes('queryParams.sortBy'), true)
  assert.equal(source.includes('queryParams.sortOrder'), true)
  assert.equal(source.includes('orderByColumn'), false)
  assert.equal(source.includes('isAsc'), false)
  assert.equal(source.includes(':default-sort'), false)
  const sortableAttrs = source.match(/sortable="[^"]*"/g) || []
  sortableAttrs.forEach(attr => {
    assert.equal(attr, 'sortable="custom"')
  })

  const sortableProps = [...source.matchAll(/prop="([^"]+)"[^>]*sortable="custom"|sortable="custom"[^>]*prop="([^"]+)"/g)]
    .map(match => match[1] || match[2])
  const expected = ['peTtm', 'pb', 'roe', 'dvTtm', 'totalMvYi', 'closePrice', 'ma120', 'priceMa120Ratio']
  expected.forEach(prop => {
    assert.equal(sortableProps.includes(prop), true, prop + ' should be sortable=custom')
  })
  assert.equal(sortableProps.includes('industry'), false)
  assert.equal(sortableProps.includes('tsCode'), false)

  assert.match(source, /label="PE"[\s\S]*sort-orders="\['ascending', 'descending'\]"/)
  assert.match(source, /label="PB"[\s\S]*sort-orders="\['ascending', 'descending'\]"/)
  assert.match(source, /label="ROE"[\s\S]*sort-orders="\['descending', 'ascending'\]"/)

  const applyQuery = source.slice(source.indexOf('applyQueryFromRoute() {'), source.indexOf('\n    syncQueryToRoute'))
  assert.match(applyQuery, /q\.sortBy/)
  assert.match(applyQuery, /q\.sortOrder/)

  const syncQuery = source.slice(source.indexOf('syncQueryToRoute() {'), source.indexOf('\n    rejectInvertedRange'))
  assert.match(syncQuery, /sortBy/)
  assert.match(syncQuery, /sortOrder/)

  const resetQuery = source.slice(source.indexOf('resetQuery() {'), source.indexOf('\n    handleExport'))
  assert.match(resetQuery, /sortBy/)
  assert.match(resetQuery, /clearSort/)

  const pageSignalWatch = source.slice(source.indexOf('pageSignal: {'), source.indexOf('isWatchlistPage: {'))
  assert.match(pageSignalWatch, /applyQueryFromRoute\(\)/)
})

test('screener mobile layout uses isMobile class, collapsed filters, and fixed stock columns', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')

  assert.equal(source.includes('screener-dashboard--mobile'), true)
  assert.equal(source.includes('isMobile'), true)
  assert.equal(source.includes("device === 'mobile'"), true)

  assert.equal(source.includes('筛选'), true)
  assert.equal(source.includes('aria-expanded'), true)
  assert.equal(source.includes('filtersExpanded'), true)

  assert.equal(source.includes(':fixed="isMobile ? \'left\' : undefined"'), true)
  assert.match(source, /:height="isMobile \? tableViewportHeight : null"/)
  assert.match(source, /ResizeObserver/)
  assert.match(source, /ref="tableViewport"/)
  assert.match(source, /table\.\$el\.style\.height = ''/)

  assert.equal(source.includes('result-table-scroller'), true)

  assert.equal(source.includes('inputmode="decimal"'), true)

  assert.equal(source.includes('label-position="top"'), false)
  assert.equal((source.match(/slot="prepend"/g) || []).length, 8)
  assert.equal(/el-button[\s\S]{0,120}type="warning"/.test(source), false)
})

test('mobile numeric ranges stay compact with fixed inner width', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')
  const style = source.slice(source.lastIndexOf('<style'))
  const mobileStart = style.indexOf('.screener-dashboard--mobile')
  assert.ok(mobileStart >= 0, 'mobile styles should exist')
  const desktop = style.slice(0, mobileStart)
  const mobile = style.slice(mobileStart)

  assert.match(desktop, /&__min[\s\S]*?\.el-input__inner[\s\S]*?width:\s*72px/)
  assert.match(desktop, /&__max[\s\S]*?\.el-input__inner[\s\S]*?width:\s*72px/)

  const mobileRange = mobile.match(/\.screener-range\s*\{[\s\S]*?\n  \.screener-toolbar__ranges/)
  assert.ok(mobileRange, 'mobile .screener-range block should exist')
  assert.match(mobileRange[0], /el-input__inner[\s\S]*width:\s*72px/)
  assert.equal(mobileRange[0].includes('width: 100%'), false)
  assert.match(mobileRange[0], /el-input-group__prepend[\s\S]*min-width:/)

  const mobileActions = mobile.match(/\.screener-toolbar__actions\s*\{[\s\S]*?\n  \}/)
  assert.ok(mobileActions, 'mobile .screener-toolbar__actions block should exist')
  assert.match(mobileActions[0], /order:/)

  assert.equal(source.includes('label-position="top"'), false)
  assert.equal((source.match(/slot="prepend"/g) || []).length, 8)
})

test('screener stock and industry columns bind mobile fixed widths', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')

  const stockColumnMatch = source.match(/<el-table-column label="股票"[\s\S]*?<\/el-table-column>/)
  assert.ok(stockColumnMatch, 'stock column template should exist')
  const stockColumn = stockColumnMatch[0]
  assert.match(stockColumn, /:width="isMobile \? 108\s*:\s*104"/)
  assert.equal(/min-width/.test(stockColumn), false)

  const industryColumnMatch = source.match(/<el-table-column label="行业"[\s\S]*?\/>/)
  assert.ok(industryColumnMatch, 'industry column template should exist')
  const industryColumn = industryColumnMatch[0]
  assert.match(industryColumn, /:width="isMobile \? 72\s*:\s*80"/)
  assert.equal(/min-width/.test(industryColumn), false)

  assert.equal(/min-width="120"/.test(source), false)
  assert.equal(/min-width="88"/.test(source), false)
  assert.equal(/label="市值"(?:\s|>)/.test(source), false)
})

test('screener desktop columns stay compact without renaming headers', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')
  const tableStart = source.indexOf('<el-table')
  const tableEnd = source.indexOf('</el-table>', tableStart)
  const table = source.slice(tableStart, tableEnd)

  assert.match(table, /<el-table-column width="44"/)
  assert.match(table, /label="股票"[\s\S]*:width="isMobile \? 108\s*:\s*104"/)
  assert.match(table, /label="股票"[\s\S]*align="left"/)
  assert.match(table, /label="行业"[\s\S]*align="left"/)
  assert.match(table, /label="行业"[\s\S]*:width="isMobile \? 72\s*:\s*80"/)
  assert.match(table, /label="PE"[\s\S]*align="right"[\s\S]*:width="isMobile \? 56\s*:\s*undefined"[\s\S]*min-width="68"/)
  assert.match(table, /label="PB"[\s\S]*align="right"[\s\S]*:width="isMobile \? 56\s*:\s*undefined"[\s\S]*min-width="68"/)
  assert.match(table, /label="ROE"[\s\S]*align="right"[\s\S]*:width="isMobile \? 56\s*:\s*undefined"[\s\S]*min-width="72"/)
  assert.match(table, /label="股息率"[\s\S]*align="right"[\s\S]*:width="isMobile \? 64\s*:\s*undefined"[\s\S]*min-width="84"/)
  assert.match(table, /:label="isMobile \? '市值' : '市值\(亿元\)'"/)
  assert.match(table, /align="right"[\s\S]*:width="isMobile \? 72\s*:\s*undefined"[\s\S]*min-width="112"/)
  assert.match(table, /label="现价"[\s\S]*align="right"[\s\S]*:width="isMobile \? 56\s*:\s*undefined"[\s\S]*min-width="68"/)
  assert.match(table, /label="MA120"[\s\S]*align="right"[\s\S]*:width="isMobile \? 64\s*:\s*undefined"[\s\S]*min-width="80"/)
  assert.match(table, /label="现价\/MA120"[\s\S]*align="right"[\s\S]*:width="isMobile \? 80\s*:\s*undefined"[\s\S]*min-width="112"/)
  assert.match(table, /label="信号"[\s\S]*align="left"[\s\S]*:width="isMobile \? 88\s*:\s*108"/)

  const stockColumn = table.match(/<el-table-column label="股票"[\s\S]*?<\/el-table-column>/)[0]
  const industryColumn = table.match(/<el-table-column label="行业"[\s\S]*?\/>/)[0]
  assert.equal(/min-width/.test(stockColumn), false)
  assert.equal(/min-width/.test(industryColumn), false)
  assert.equal(table.includes('width="52"'), false)
  assert.equal(table.includes('min-width="148"'), false)
  assert.equal(/min-width="88"/.test(table), false)
  assert.equal(table.includes('width="92"'), false)
  assert.equal(table.includes('width="100"'), false)
  assert.equal(/\swidth="120"/.test(table), false)
  assert.equal(table.includes('width="130"'), false)
  assert.equal(/label="市值"(?:\s|>)/.test(table), false)
  assert.equal(table.includes('label="价/MA"'), false)

  const style = source.slice(source.lastIndexOf('<style'))
  const desktop = style.slice(0, style.indexOf('.screener-dashboard--mobile'))
  const tableStyle = desktop.slice(desktop.indexOf('.result-table {'))
  assert.match(tableStyle, /th > \.cell[\s\S]*padding-left:\s*8px/)
  assert.match(tableStyle, /th > \.cell[\s\S]*padding-right:\s*8px/)
  assert.match(tableStyle, /th > \.cell[\s\S]*white-space:\s*nowrap/)
  assert.equal(/padding-left:\s*12px/.test(tableStyle.slice(0, tableStyle.indexOf('.stock-cell'))), false)
})

test('screener mobile table fills remaining viewport and does not use overflow-x scroller', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')
  const style = source.slice(source.lastIndexOf('<style'))
  const mobileStart = style.indexOf('.screener-dashboard--mobile')
  assert.ok(mobileStart >= 0, 'mobile styles should exist')
  const mobile = style.slice(mobileStart)

  const scroller = mobile.match(/\.result-table-scroller\s*\{[\s\S]*?\n  \}/)
  assert.ok(scroller, 'mobile .result-table-scroller block should exist')
  assert.match(scroller[0], /overflow:\s*hidden/)
  assert.match(scroller[0], /height:\s*100%/)
  assert.equal(scroller[0].includes('overflow-x: auto'), false)

  assert.match(mobile, /display:\s*flex/)
  assert.match(mobile, /flex:\s*1/)
  assert.match(mobile, /min-height:\s*0/)
})

test('screener stock name links to Xueqiu in a new tab', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')
  assert.equal(source.includes('xueqiuQuoteUrl'), true)
  assert.equal(source.includes('stock-cell__name--link'), true)
  assert.equal(source.includes('target="_blank"'), true)
  assert.equal(source.includes('rel="noopener noreferrer"'), true)

  const stockColumnMatch = source.match(/<el-table-column label="股票"[\s\S]*?<\/el-table-column>/)
  assert.ok(stockColumnMatch, 'stock column template should exist')
  const stockColumn = stockColumnMatch[0]
  assert.match(stockColumn, /<a[\s\S]*class="stock-cell__name stock-cell__name--link"/)
  assert.match(stockColumn, /v-if="xueqiuQuoteUrl\(scope\.row\.tsCode\)"/)
  assert.equal(stockColumn.includes('target="_blank"'), true)
  assert.equal(stockColumn.includes('rel="noopener noreferrer"'), true)
  assert.match(stockColumn, /<div class="stock-cell__code">\{\{\s*scope\.row\.tsCode/)
  assert.equal(/stock-cell__code[\s\S]{0,80}<a/.test(stockColumn), false)

  const linkStyleStart = source.indexOf('a.stock-cell__name--link {')
  assert.ok(linkStyleStart >= 0, 'name link selector should beat Element table anchors')
  const linkStyle = source.slice(linkStyleStart, source.indexOf('.stock-cell__code {', linkStyleStart))
  const defaultBlock = linkStyle.slice(0, linkStyle.indexOf('&:hover'))
  assert.match(defaultBlock, /font-weight:\s*700/)
  assert.match(defaultBlock, /color:\s*\$color-primary/)
  assert.match(defaultBlock, /cursor:\s*pointer/)
  assert.equal(defaultBlock.includes('text-decoration: underline'), false)
  assert.match(linkStyle, /&:visited[\s\S]*color:\s*\$color-primary/)
  assert.match(linkStyle, /\$color-primary-hover/)
  assert.match(linkStyle, /text-underline-offset/)
  assert.match(linkStyle, /&:focus-visible[\s\S]*outline:\s*2px solid \$color-ring/)
})
