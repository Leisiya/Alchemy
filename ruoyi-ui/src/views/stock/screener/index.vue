<template>
  <div class="app-container screener-dashboard" :class="{ 'screener-dashboard--mobile': isMobile }">
    <div class="detail-card">
      <div class="detail-header">
        <div class="detail-heading">
          <h1 class="detail-title">{{ pageTitle }}</h1>
          <p v-if="pageRuleHint" class="detail-rule-hint">{{ pageRuleHint }}</p>
        </div>
        <div class="detail-actions">
          <span
            v-if="updatedAtLabel"
            class="detail-updated-at"
            role="status"
            aria-atomic="true"
          >{{ updatedAtLabel }}</span>
          <el-button
            v-if="!isWatchlistPage"
            plain
            icon="el-icon-download"
            size="small"
            :loading="exporting"
            :disabled="exporting"
            @click="handleExport"
            v-hasPermi="['stock:screener:export']"
          >
            导出
          </el-button>
        </div>
      </div>

      <el-alert
        v-if="latestRunStatus && latestRunStatus.status === '1'"
        :title="`最近一次任务失败：${latestRunStatus.errorMessage || '未返回错误详情'}，当前仍展示上一次成功快照。`"
        type="warning"
        :closable="false"
        class="mb16"
      />

      <guest-watchlist-lock v-if="isGuest && isWatchlistPage" />

      <template v-if="!(isGuest && isWatchlistPage)">
      <button
        v-if="isMobile"
        type="button"
        class="screener-filter-toggle"
        :aria-expanded="filtersExpanded ? 'true' : 'false'"
        @click="filtersExpanded = !filtersExpanded"
      >筛选</button>
      <el-form
        v-show="!isMobile || filtersExpanded"
        :model="queryParams"
        ref="queryForm"
        size="small"
        class="screener-toolbar"
        @submit.native.prevent="handleQuery"
      >
        <div class="screener-toolbar__row">
          <el-form-item prop="tsCode">
            <el-input
              v-model="queryParams.tsCode"
              placeholder="请输入"
              clearable
              @keyup.enter.native="handleQuery"
            >
              <template slot="prepend">代码</template>
            </el-input>
          </el-form-item>
          <el-form-item prop="name">
            <el-input
              v-model="queryParams.name"
              placeholder="请输入"
              clearable
              @keyup.enter.native="handleQuery"
            >
              <template slot="prepend">名称</template>
            </el-input>
          </el-form-item>
          <el-form-item prop="industry">
            <el-input
              v-model="queryParams.industry"
              placeholder="请输入"
              clearable
              @keyup.enter.native="handleQuery"
            >
              <template slot="prepend">行业</template>
            </el-input>
          </el-form-item>
          <el-form-item class="screener-toolbar__actions">
            <el-button native-type="submit" type="primary" icon="el-icon-search" size="small">搜索</el-button>
            <el-button native-type="button" icon="el-icon-refresh" size="small" @click="resetQuery">重置</el-button>
          </el-form-item>
        </div>
        <div class="screener-toolbar__row screener-toolbar__ranges">
          <el-form-item prop="peTtmMin">
            <div class="screener-range">
              <el-input
                class="screener-range__min"
                v-model="queryParams.peTtmMin"
                placeholder="最低"
                clearable
                inputmode="decimal"
                @keyup.enter.native="handleQuery"
              >
                <template slot="prepend">PE</template>
              </el-input>
              <span class="screener-range__sep" aria-hidden="true">—</span>
              <el-input
                class="screener-range__max"
                v-model="queryParams.peTtmMax"
                placeholder="最高"
                clearable
                inputmode="decimal"
                @keyup.enter.native="handleQuery"
              />
            </div>
          </el-form-item>
          <el-form-item prop="pbMin">
            <div class="screener-range">
              <el-input
                class="screener-range__min"
                v-model="queryParams.pbMin"
                placeholder="最低"
                clearable
                inputmode="decimal"
                @keyup.enter.native="handleQuery"
              >
                <template slot="prepend">PB</template>
              </el-input>
              <span class="screener-range__sep" aria-hidden="true">—</span>
              <el-input
                class="screener-range__max"
                v-model="queryParams.pbMax"
                placeholder="最高"
                clearable
                inputmode="decimal"
                @keyup.enter.native="handleQuery"
              />
            </div>
          </el-form-item>
          <el-form-item prop="roeMin">
            <div class="screener-range">
              <el-input
                class="screener-range__min"
                v-model="queryParams.roeMin"
                placeholder="最低"
                clearable
                inputmode="decimal"
                @keyup.enter.native="handleQuery"
              >
                <template slot="prepend">ROE</template>
              </el-input>
              <span class="screener-range__sep" aria-hidden="true">—</span>
              <el-input
                class="screener-range__max"
                v-model="queryParams.roeMax"
                placeholder="最高"
                clearable
                inputmode="decimal"
                @keyup.enter.native="handleQuery"
              />
            </div>
          </el-form-item>
          <el-form-item prop="dvTtmMin">
            <div class="screener-range">
              <el-input
                class="screener-range__min"
                v-model="queryParams.dvTtmMin"
                placeholder="最低"
                clearable
                inputmode="decimal"
                @keyup.enter.native="handleQuery"
              >
                <template slot="prepend">股息率</template>
              </el-input>
              <span class="screener-range__sep" aria-hidden="true">—</span>
              <el-input
                class="screener-range__max"
                v-model="queryParams.dvTtmMax"
                placeholder="最高"
                clearable
                inputmode="decimal"
                @keyup.enter.native="handleQuery"
              />
            </div>
          </el-form-item>
          <el-form-item prop="totalMvYiMin">
            <div class="screener-range">
              <el-input
                class="screener-range__min"
                v-model="queryParams.totalMvYiMin"
                placeholder="最低"
                clearable
                inputmode="decimal"
                @keyup.enter.native="handleQuery"
              >
                <template slot="prepend">市值</template>
              </el-input>
              <span class="screener-range__sep" aria-hidden="true">—</span>
              <el-input
                class="screener-range__max"
                v-model="queryParams.totalMvYiMax"
                placeholder="最高"
                clearable
                inputmode="decimal"
                @keyup.enter.native="handleQuery"
              />
            </div>
          </el-form-item>
        </div>
      </el-form>

      <div class="result-table-region" :aria-busy="loading ? 'true' : 'false'">
        <div ref="tableViewport" class="result-table-scroller">
        <el-table
          ref="resultTable"
          v-loading="showTableLoading"
          :data="resultList"
          class="result-table"
          :empty-text="tableEmptyText"
          :height="isMobile ? tableViewportHeight : null"
          @sort-change="handleSortChange"
        >
          <el-table-column width="44" align="center" :fixed="isMobile ? 'left' : undefined">
            <template slot-scope="scope">
              <el-button
                type="text"
                class="watchlist-star"
                :class="{ 'watchlist-star--active': isWatched(scope.row.tsCode) }"
                :aria-label="isGuest ? '加入自选需要注册' : (isWatched(scope.row.tsCode) ? '移出自选' : '加入自选')"
                @click="toggleWatchlist(scope.row)"
              >
                <i :class="isWatched(scope.row.tsCode) ? 'el-icon-star-on' : 'el-icon-star-off'" />
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="股票" :width="isMobile ? 108 : 104" align="left" :fixed="isMobile ? 'left' : undefined">
            <template slot-scope="scope">
              <div class="stock-cell">
                <a
                  v-if="xueqiuQuoteUrl(scope.row.tsCode)"
                  class="stock-cell__name stock-cell__name--link"
                  :href="xueqiuQuoteUrl(scope.row.tsCode)"
                  target="_blank"
                  rel="noopener noreferrer"
                >{{ scope.row.name || '—' }}</a>
                <div v-else class="stock-cell__name">{{ scope.row.name || '—' }}</div>
                <div class="stock-cell__code">{{ scope.row.tsCode || '—' }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="行业" align="left" prop="industry" :width="isMobile ? 72 : 80" :show-overflow-tooltip="!isMobile" />
          <el-table-column label="PE" align="right" :width="isMobile ? 56 : undefined" min-width="68" prop="peTtm" sortable="custom" :sort-orders="['ascending', 'descending']">
            <template slot-scope="scope">
              <span class="num-cell">{{ formatDecimal(scope.row.peTtm) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="PB" align="right" :width="isMobile ? 56 : undefined" min-width="68" prop="pb" sortable="custom" :sort-orders="['ascending', 'descending']">
            <template slot-scope="scope">
              <span class="num-cell">{{ formatDecimal(scope.row.pb) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="ROE" align="right" :width="isMobile ? 56 : undefined" min-width="72" prop="roe" sortable="custom" :sort-orders="['descending', 'ascending']">
            <template slot-scope="scope">
              <span class="num-cell">{{ formatPercent(scope.row.roe) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="股息率" align="right" :width="isMobile ? 64 : undefined" min-width="84" prop="dvTtm" sortable="custom" :sort-orders="['descending', 'ascending']">
            <template slot-scope="scope">
              <span v-if="formatPercent(scope.row.dvTtm) !== '—'" class="metric-badge">{{ formatPercent(scope.row.dvTtm) }}</span>
              <span v-else class="num-cell">—</span>
            </template>
          </el-table-column>
          <el-table-column :label="isMobile ? '市值' : '市值(亿元)'" align="right" :width="isMobile ? 72 : undefined" min-width="112" prop="totalMvYi" sortable="custom" :sort-orders="['descending', 'ascending']">
            <template slot-scope="scope">
              <span class="num-cell">{{ formatThousands(scope.row.totalMvYi) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="现价" align="right" :width="isMobile ? 56 : undefined" min-width="68" prop="closePrice" sortable="custom" :sort-orders="['descending', 'ascending']">
            <template slot-scope="scope">
              <span class="num-cell">{{ formatDecimal(scope.row.closePrice) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="MA120" align="right" :width="isMobile ? 64 : undefined" min-width="80" prop="ma120" sortable="custom" :sort-orders="['descending', 'ascending']">
            <template slot-scope="scope">
              <span class="num-cell">{{ formatDecimal(scope.row.ma120) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="现价/MA120" align="right" :width="isMobile ? 80 : undefined" min-width="112" prop="priceMa120Ratio" sortable="custom" :sort-orders="['descending', 'ascending']">
            <template slot-scope="scope">
              <span class="num-cell">{{ formatDecimal(scope.row.priceMa120Ratio) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="信号" align="left" :width="isMobile ? 88 : 108">
            <template slot-scope="scope">
              <span
                v-if="scope.row.outOfPool"
                class="signal-chip signal-chip--muted"
              >已不在候选池</span>
              <span
                v-else-if="scope.row.ma120Signal === '破位低估'"
                class="signal-chip signal-chip--low"
              >破位低估</span>
              <span
                v-else-if="scope.row.ma120Signal === '强势突破'"
                class="signal-chip signal-chip--high"
              >强势突破</span>
              <span
                v-else
                class="signal-chip signal-chip--muted"
              >有待观察</span>
            </template>
          </el-table-column>
        </el-table>
        </div>
      </div>

      <pagination
        v-show="total > 0"
        :total="total"
        :page.sync="queryParams.pageNum"
        :limit.sync="queryParams.pageSize"
        @pagination="handlePagination"
      />
      </template>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex"
import { getLatestScreenDashboard, listScreenResults } from "@/api/stock/screener"
import { addWatchlist, listWatchlist, listWatchlistCodes, removeWatchlist } from "@/api/stock/watchlist"
import { formatDecimal, formatPercent, formatThousands, formatSnapshotFreshness } from "@/utils/formatScreenMetrics"
import { xueqiuQuoteUrl } from "@/utils/xueqiuQuoteUrl"
import {
  METRIC_RANGE_FIELDS,
  hasInvalidRange,
  hasInvertedRange,
  omitBlankRanges,
  pickRangeQuery
} from "@/utils/metricRangeFilters"
import GuestWatchlistLock from "./GuestWatchlistLock"

export default {
  name: "StockScreener",
  components: { GuestWatchlistLock },
  data() {
    return {
      loading: false,
      filtersExpanded: false,
      tableViewportHeight: undefined,
      tableHeightObserver: null,
      showTableLoading: false,
      loadingTimer: null,
      nowMs: Date.now(),
      freshnessTimer: null,
      exporting: false,
      total: 0,
      resultList: [],
      watchlistCodes: [],
      latestRun: null,
      latestRunStatus: null,
      queryParams: {
        pageNum: 1,
        pageSize: 20,
        signal: "",
        tsCode: undefined,
        name: undefined,
        industry: undefined,
        peTtmMin: undefined,
        peTtmMax: undefined,
        pbMin: undefined,
        pbMax: undefined,
        roeMin: undefined,
        roeMax: undefined,
        dvTtmMin: undefined,
        dvTtmMax: undefined,
        totalMvYiMin: undefined,
        totalMvYiMax: undefined,
        sortBy: undefined,
        sortOrder: undefined
      }
    }
  },
  computed: {
    ...mapGetters(["isGuest", "device"]),
    isMobile() {
      return this.device === 'mobile'
    },
    pageTitle() {
      return (this.$route.meta && this.$route.meta.title) || "股票列表"
    },
    pageSignal() {
      return (this.$route.meta && this.$route.meta.signal) || ""
    },
    isWatchlistPage() {
      return !!(this.$route.meta && this.$route.meta.watchlist)
    },
    pageRuleHint() {
      if (this.isWatchlistPage) {
        return ""
      }
      if (this.pageSignal === "破位低估") {
        return "现价/MA120 < 0.88"
      }
      if (this.pageSignal === "强势突破") {
        return "现价/MA120 > 1.12"
      }
      return "PE < 20 · 股息率 > 3% · 市值 > 50 亿"
    },
    updatedAtLabel() {
      return formatSnapshotFreshness(
        this.latestRun && this.latestRun.tradeDate,
        this.latestRun && this.latestRun.finishedAt,
        this.nowMs
      )
    },
    tableEmptyText() {
      if (this.isWatchlistPage && !this.watchlistCodes.length) {
        return "还没有自选股票，可在股票列表中点击星标加入。"
      }
      if (!this.latestRun) {
        return "暂无成功的筛股快照，请等待定时任务执行。"
      }
      return "没有符合条件的股票"
    }
  },
  watch: {
    isMobile() {
      this.$nextTick(() => {
        this.bindTableHeightObserver()
        this.clearDesktopTableHeight()
        this.relayoutResultTable()
      })
    },
    pageSignal: {
      immediate: false,
      handler() {
        this.queryParams.signal = this.pageSignal
        this.queryParams.pageNum = 1
        this.applyQueryFromRoute()
        this.getList()
      }
    },
    isWatchlistPage: {
      immediate: false,
      handler() {
        this.queryParams.signal = this.pageSignal
        this.queryParams.pageNum = 1
        this.applyQueryFromRoute()
        this.loadWatchlistCodes().then(() => this.getList())
      }
    }
  },
  created() {
    this.queryParams.signal = this.pageSignal
    this.applyQueryFromRoute()
    this.loadWatchlistCodes().then(() => this.initializePage())
    this.freshnessTimer = setInterval(() => {
      this.nowMs = Date.now()
    }, 60000)
  },
  mounted() {
    this.bindTableHeightObserver()
  },
  activated() {
    this.queryParams.signal = this.pageSignal
    this.applyQueryFromRoute()
    this.loadWatchlistCodes().then(() => this.getList())
    this.$nextTick(() => this.bindTableHeightObserver())
  },
  beforeDestroy() {
    clearTimeout(this.loadingTimer)
    clearInterval(this.freshnessTimer)
    this.unbindTableHeightObserver()
  },
  methods: {
    relayoutResultTable() {
      this.$refs.resultTable && this.$refs.resultTable.doLayout()
    },
    clearDesktopTableHeight() {
      if (this.isMobile) {
        return
      }
      const table = this.$refs.resultTable
      if (table && table.$el) {
        table.$el.style.height = ''
      }
    },
    bindTableHeightObserver() {
      this.unbindTableHeightObserver()
      const el = this.$refs.tableViewport
      if (!el || typeof ResizeObserver === 'undefined') {
        return
      }
      this.tableHeightObserver = new ResizeObserver((entries) => {
        const entry = entries[0]
        if (!entry) {
          return
        }
        const next = Math.floor(entry.contentRect.height)
        if (next <= 0) {
          return
        }
        if (next !== this.tableViewportHeight) {
          this.tableViewportHeight = next
        }
        this.$nextTick(() => this.relayoutResultTable())
      })
      this.tableHeightObserver.observe(el)
    },
    unbindTableHeightObserver() {
      if (this.tableHeightObserver) {
        this.tableHeightObserver.disconnect()
        this.tableHeightObserver = null
      }
    },
    formatDecimal,
    formatThousands,
    formatPercent,
    xueqiuQuoteUrl,
    isWatched(tsCode) {
      return this.watchlistCodes.indexOf(tsCode) !== -1
    },
    loadWatchlistCodes() {
      if (this.isGuest) {
        this.watchlistCodes = []
        return Promise.resolve()
      }
      return listWatchlistCodes().then(response => {
        this.watchlistCodes = Array.isArray(response.data) ? response.data : []
      }).catch(() => {
        this.watchlistCodes = []
      })
    },
    applyQueryFromRoute() {
      const q = this.$route.query || {}
      this.queryParams.tsCode = q.tsCode || undefined
      this.queryParams.name = q.name || undefined
      this.queryParams.industry = q.industry || undefined
      const pageNum = parseInt(q.pageNum, 10)
      this.queryParams.pageNum = pageNum > 0 ? pageNum : 1
      METRIC_RANGE_FIELDS.forEach(field => {
        this.queryParams[field.minKey] = undefined
        this.queryParams[field.maxKey] = undefined
      })
      Object.assign(this.queryParams, pickRangeQuery(q))
      const allowedSort = {
        peTtm: true,
        pb: true,
        roe: true,
        dvTtm: true,
        totalMvYi: true,
        closePrice: true,
        ma120: true,
        priceMa120Ratio: true
      }
      const sortBy = q.sortBy
      const sortOrder = q.sortOrder
      if (allowedSort[sortBy] && (sortOrder === 'asc' || sortOrder === 'desc')) {
        this.queryParams.sortBy = sortBy
        this.queryParams.sortOrder = sortOrder
      } else {
        this.queryParams.sortBy = undefined
        this.queryParams.sortOrder = undefined
      }
    },
    syncQueryToRoute() {
      const query = {}
      if (this.queryParams.tsCode) query.tsCode = this.queryParams.tsCode
      if (this.queryParams.name) query.name = this.queryParams.name
      if (this.queryParams.industry) query.industry = this.queryParams.industry
      if (this.queryParams.pageNum && this.queryParams.pageNum !== 1) {
        query.pageNum = String(this.queryParams.pageNum)
      }
      Object.assign(query, pickRangeQuery(this.queryParams))
      if (this.queryParams.sortBy && this.queryParams.sortOrder) {
        query.sortBy = this.queryParams.sortBy
        query.sortOrder = this.queryParams.sortOrder
      }
      const current = this.$route.query || {}
      const keys = new Set([...Object.keys(current), ...Object.keys(query)])
      let same = true
      keys.forEach(key => {
        if (String(current[key] || "") !== String(query[key] || "")) {
          same = false
        }
      })
      if (same) {
        return
      }
      this.$router.replace({ path: this.$route.path, query }).catch(() => {})
    },
    rejectInvertedRange() {
      const invalid = hasInvalidRange(this.queryParams)
      if (invalid) {
        this.$modal.msgError(invalid + "：请输入有效数字")
        return true
      }
      const inverted = hasInvertedRange(this.queryParams)
      if (inverted) {
        this.$modal.msgError(inverted + "：最低不能大于最高")
        return true
      }
      return false
    },
    setListLoading(on) {
      if (on) {
        this.loading = true
        clearTimeout(this.loadingTimer)
        this.loadingTimer = setTimeout(() => {
          this.showTableLoading = true
        }, 200)
      } else {
        this.loading = false
        clearTimeout(this.loadingTimer)
        this.showTableLoading = false
      }
    },
    initializePage() {
      this.setListLoading(true)
      getLatestScreenDashboard().then(response => {
        const data = response.data || {}
        this.latestRun = data.latestRun || null
        this.latestRunStatus = data.latestRunStatus || null
        this.getList()
      }).catch(() => {
        if (this.isWatchlistPage) {
          this.getList()
          return
        }
        this.setListLoading(false)
      })
    },
    getList() {
      if (this.rejectInvertedRange()) {
        this.setListLoading(false)
        return
      }
      this.setListLoading(true)
      if (this.isGuest && this.isWatchlistPage) {
        this.resultList = []
        this.total = 0
        this.setListLoading(false)
        return
      }
      if (this.isWatchlistPage) {
        const { signal, ...params } = omitBlankRanges(this.queryParams)
        listWatchlist(params).then(response => {
          this.resultList = response.rows
          this.total = response.total
          this.setListLoading(false)
          this.syncQueryToRoute()
        }).catch(() => {
          this.setListLoading(false)
        })
        return
      }
      const params = omitBlankRanges({ ...this.queryParams, signal: this.pageSignal })
      listScreenResults(params).then(response => {
        this.resultList = response.rows
        this.total = response.total
        this.setListLoading(false)
        this.syncQueryToRoute()
      }).catch(() => {
        this.setListLoading(false)
      })
    },
    toggleWatchlist(row) {
      if (this.isGuest) {
        this.$modal.msgWarning('自选功能需要注册')
        return
      }
      const tsCode = row.tsCode
      if (this.isWatched(tsCode)) {
        removeWatchlist(tsCode).then(() => {
          this.watchlistCodes = this.watchlistCodes.filter(code => code !== tsCode)
          if (this.isWatchlistPage) {
            this.getList()
          }
          this.$modal.msgSuccess("已移出自选")
        })
        return
      }
      addWatchlist(tsCode).then(() => {
        this.watchlistCodes = this.watchlistCodes.concat(tsCode)
        this.$modal.msgSuccess("已加入自选")
      })
    },
    handleQuery() {
      this.queryParams.pageNum = 1
      this.getList()
    },
    handlePagination() {
      this.getList()
    },
    handleSortChange({ column, prop, order }) {
      const sortProp = prop || (column && column.property)
      if (!order || !sortProp) {
        this.queryParams.sortBy = undefined
        this.queryParams.sortOrder = undefined
      } else {
        this.queryParams.sortBy = sortProp
        this.queryParams.sortOrder = order === 'ascending' ? 'asc' : 'desc'
      }
      this.queryParams.pageNum = 1
      this.getList()
    },
    resetQuery() {
      this.resetForm("queryForm")
      this.queryParams.signal = this.pageSignal
      this.queryParams.tsCode = undefined
      this.queryParams.name = undefined
      this.queryParams.industry = undefined
      this.queryParams.pageNum = 1
      METRIC_RANGE_FIELDS.forEach(field => {
        this.queryParams[field.minKey] = undefined
        this.queryParams[field.maxKey] = undefined
      })
      this.queryParams.sortBy = undefined
      this.queryParams.sortOrder = undefined
      if (this.$refs.resultTable) {
        this.$refs.resultTable.clearSort()
      }
      this.getList()
    },
    handleExport() {
      if (this.exporting) {
        return
      }
      if (this.rejectInvertedRange()) {
        return
      }
      this.exporting = true
      const exportParams = omitBlankRanges({
        ...this.queryParams,
        signal: this.pageSignal
      })
      delete exportParams.pageNum
      delete exportParams.pageSize
      const done = this.download("stock/screener/results/export", exportParams, `screen_results_${new Date().getTime()}.xlsx`)
      Promise.resolve(done).finally(() => {
        this.exporting = false
      })
    }
  }
}
</script>

<style scoped lang="scss">
@import "~@/assets/styles/tokens.scss";

.screener-dashboard {
  background: $color-background;
  min-height: calc(100vh - 84px);
  padding: $space-2xl;
}

.detail-card {
  background: $color-card;
  border-radius: $radius-lg;
  box-shadow: $shadow-card;
  color: inherit;
  text-decoration: none;
  padding: $space-2xl $space-2xl $space-lg;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $space-xl;
  margin-bottom: $space-xl;
}

.detail-heading {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: $space-lg;
  min-width: 0;
  flex: 1;
}

.detail-title {
  margin: 0;
  font-size: $font-title;
  font-weight: 700;
  line-height: 1.2;
  color: $color-foreground;
  flex-shrink: 0;
}

.detail-rule-hint {
  margin: 0;
  font-size: $font-meta;
  font-weight: 400;
  line-height: 1.4;
  color: $color-muted-foreground;
  min-width: 0;
}

.detail-updated-at {
  font-size: $font-meta;
  color: $color-muted-foreground;
  white-space: nowrap;
}

.detail-actions {
  display: flex;
  align-items: center;
  gap: $space-lg;
  flex-shrink: 0;
}

.screener-toolbar {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: $space-lg;
  margin-bottom: $space-xl;

  &__row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: $space-lg;
  }

  ::v-deep .el-form-item {
    margin: 0;
  }

  ::v-deep .el-form-item__content {
    margin-left: 0 !important;
    line-height: 32px;
  }

  ::v-deep .el-input {
    width: 200px;
  }

  ::v-deep .el-input-group__prepend {
    background-color: $color-card;
    color: $color-muted-foreground;
    border-color: $color-border;
    border-right: 1px solid $color-border;
    padding: 0 10px;
    font-size: $font-meta;
    font-weight: 500;
    height: 32px;
    line-height: 30px;
    white-space: nowrap;
  }

  ::v-deep .el-input-group--prepend .el-input__inner {
    border-left: 0;
    height: 32px;
    line-height: 32px;
  }

  ::v-deep .el-input-group:focus-within .el-input-group__prepend,
  ::v-deep .el-input-group:focus-within .el-input__inner {
    border-color: $color-ring;
  }

  &__actions {
    ::v-deep .el-form-item__content {
      display: flex;
      align-items: center;
      gap: $space-sm;
    }
  }

  &__ranges {
    ::v-deep .el-input {
      width: auto;
    }

    ::v-deep .el-input__inner {
      height: 32px;
      line-height: 32px;
    }
  }
}

.screener-range {
  display: inline-flex;
  align-items: stretch;
  height: 32px;

  &__min {
    ::v-deep .el-input__inner {
      width: 72px;
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
      border-right: 0;
    }
  }

  &__sep {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 16px;
    padding: 0 4px;
    border-top: 1px solid $color-border;
    border-bottom: 1px solid $color-border;
    background: $color-card;
    color: $color-muted-foreground;
    font-size: $font-meta;
    line-height: 30px;
    box-sizing: border-box;
  }

  &__max {
    ::v-deep .el-input__inner {
      width: 72px;
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
      border-left: 0;
    }
  }

  &:focus-within {
    .screener-range__sep {
      border-color: $color-ring;
    }

    ::v-deep .el-input-group__prepend,
    ::v-deep .el-input__inner {
      border-color: $color-ring;
    }
  }
}

.result-table {
  width: 100%;

  ::v-deep th,
  ::v-deep td {
    font-size: $font-num;
    color: $color-foreground;
  }

  ::v-deep th {
    font-size: $font-meta;
    font-weight: 500;
    color: $color-muted-foreground;
    background: $color-card;
  }

  ::v-deep th > .cell,
  ::v-deep td > .cell {
    padding-left: 8px;
    padding-right: 8px;
  }

  ::v-deep th > .cell {
    white-space: nowrap;
  }

  ::v-deep td {
    padding: 8px 0;
    height: $table-row-height;
  }

  ::v-deep .el-table__body tr:hover > td {
    background-color: #f8fafc !important;
  }

  ::v-deep td,
  ::v-deep th.is-leaf {
    border-bottom: 1px solid $color-border;
  }
}

.stock-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.watchlist-star {
  padding: 0;
  border: 0;
  background: transparent;
  color: $color-muted-foreground;
  font-size: 18px;

  &:hover,
  &:focus {
    color: $color-primary;
  }

  &--active {
    color: $color-primary;
  }
}

.stock-cell__name {
  font-size: $font-body;
  font-weight: 700;
  line-height: 1.3;
  color: $color-foreground;
}

a.stock-cell__name--link {
  font-weight: 700;
  color: $color-primary;
  text-decoration: none;
  cursor: pointer;

  &:visited {
    color: $color-primary;
  }

  &:hover,
  &:focus {
    color: $color-primary-hover;
    text-decoration: underline;
    text-underline-offset: 3px;
    text-decoration-thickness: 1px;
  }

  &:focus-visible {
    outline: 2px solid $color-ring;
    outline-offset: 2px;
  }
}

.stock-cell__code {
  font-size: $font-meta;
  line-height: 1.3;
  color: $color-muted-foreground;
}

.num-cell {
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum";
  font-size: $font-num;
}

.metric-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 56px;
  padding: 2px 4px;
  border-radius: $radius-md;
  background: rgba(21, 128, 61, 0.12);
  color: $color-primary;
  font-size: $font-meta;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.signal-chip {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: $radius-md;
  font-size: $font-meta;
  font-weight: 600;
  line-height: 1.4;
  white-space: nowrap;
}

.signal-chip--low {
  background: #fff7ed;
  color: #c2410c;
}

.signal-chip--high {
  background: rgba(21, 128, 61, 0.12);
  color: $color-primary-hover;
}

.signal-chip--muted {
  background: $color-muted;
  color: $color-muted-foreground;
}

.mb16 {
  margin-bottom: $space-xl;
}

@media (max-width: 1199px) {
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .detail-heading {
    width: 100%;
  }
}

.screener-dashboard--mobile {
  padding: 0;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .detail-card {
    padding: $space-xl;
    border-radius: 0;
    box-shadow: none;
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .detail-header,
  .el-alert,
  .screener-filter-toggle,
  .screener-toolbar,
  .pagination-container {
    flex-shrink: 0;
  }

  .result-table-region {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .detail-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .detail-updated-at {
    white-space: normal;
  }

  .screener-filter-toggle {
    display: block;
    width: 100%;
    min-height: 44px;
    margin-bottom: $space-lg;
    padding: 0 $space-lg;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    background: $color-card;
    color: $color-foreground;
    font-size: $font-body;
    cursor: pointer;
  }

  .screener-toolbar ::v-deep .el-input {
    width: 100%;
  }

  .screener-toolbar ::v-deep .el-form-item {
    width: 100%;
  }

  .screener-toolbar__row {
    display: contents;
  }

  .screener-toolbar ::v-deep .el-input__inner {
    font-size: 16px;
  }

  .screener-toolbar__actions {
    order: 1;

    ::v-deep .el-form-item__content {
      display: flex;
      gap: $space-md;
    }

    ::v-deep .el-button {
      flex: 1;
      min-height: 44px;
    }
  }

  .screener-range {
    display: inline-flex;
    align-items: stretch;
    width: auto;
    height: 32px;

    ::v-deep .el-input-group__prepend {
      min-width: 56px;
      height: 32px;
      line-height: 30px;
      box-sizing: border-box;
    }

    &__min,
    &__max {
      ::v-deep .el-input__inner {
        width: 72px;
      }
    }

    &__sep {
      flex: 0 0 auto;
    }
  }

  .screener-toolbar__ranges ::v-deep .el-input {
    width: auto;
  }

  .result-table-scroller {
    flex: 1;
    min-height: 0;
    height: 100%;
    overflow: hidden;
  }

  .watchlist-star {
    min-width: 44px;
    min-height: 44px;
  }

  ::v-deep .el-pagination__total {
    display: none;
  }
}
</style>
