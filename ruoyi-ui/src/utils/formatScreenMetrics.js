import { parseTime } from './ruoyi.js'

const EMPTY = '—'

function isBlank(value) {
  if (value === null || value === undefined) {
    return true
  }
  if (typeof value === 'string' && value.trim() === '') {
    return true
  }
  return false
}

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : null
}

export function formatDecimal(value, digits = 2) {
  const n = isBlank(value) ? null : toNumber(value)
  if (n === null) {
    return EMPTY
  }
  return n.toFixed(digits)
}

export function formatThousands(value, digits = 2) {
  const formatted = formatDecimal(value, digits)
  if (formatted === EMPTY) {
    return EMPTY
  }
  const negative = formatted.charAt(0) === '-'
  const unsigned = negative ? formatted.slice(1) : formatted
  const parts = unsigned.split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  const joined = parts.join('.')
  return negative ? '-' + joined : joined
}

export function formatPercent(value, digits = 2) {
  const formatted = formatDecimal(value, digits)
  if (formatted === EMPTY) {
    return EMPTY
  }
  return formatted + '%'
}

export function formatTradeDate(value) {
  if (isBlank(value)) {
    return ''
  }
  const text = String(value).trim()
  if (/^\d{8}$/.test(text)) {
    return text.slice(0, 4) + '-' + text.slice(4, 6) + '-' + text.slice(6, 8)
  }
  return text
}

export function formatCount(value) {
  const n = isBlank(value) ? null : toNumber(value)
  if (n === null) {
    return EMPTY
  }
  return String(Math.trunc(n))
}

const UPDATED_AT_PATTERN = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/
const NAIVE_DATETIME = /^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}$/
const MINUTE_MS = 60 * 1000
const HOUR_MS = 60 * MINUTE_MS
const DAY_MS = 24 * HOUR_MS

function shanghaiYmd(ms) {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).formatToParts(new Date(ms))
  const map = {}
  parts.forEach(part => {
    if (part.type !== 'literal') {
      map[part.type] = part.value
    }
  })
  return map.year + map.month + map.day
}

function ymdUtcMs(ymd) {
  return Date.UTC(Number(ymd.slice(0, 4)), Number(ymd.slice(4, 6)) - 1, Number(ymd.slice(6, 8)))
}

function toTimestamp(value) {
  if (value instanceof Date) {
    const ms = value.getTime()
    return Number.isFinite(ms) ? ms : NaN
  }
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : NaN
  }
  if (typeof value !== 'string') {
    return NaN
  }
  const text = value.trim()
  if (NAIVE_DATETIME.test(text)) {
    return Date.parse(text.replace(' ', 'T') + '+08:00')
  }
  const parsed = Date.parse(text)
  if (Number.isFinite(parsed)) {
    return parsed
  }
  const fallback = new Date(text.replace(/-/g, '/').replace('T', ' '))
  return fallback.getTime()
}

function formatCloseDateLabel(tradeDate, now) {
  const text = String(tradeDate).trim()
  if (!/^\d{8}$/.test(text)) {
    return ''
  }
  const year = Number(text.slice(0, 4))
  const month = Number(text.slice(4, 6))
  const day = Number(text.slice(6, 8))
  const nowYear = Number(shanghaiYmd(now).slice(0, 4))
  if (year === nowYear) {
    return month + '月' + day + '日'
  }
  return year + '年' + month + '月' + day + '日'
}

function formatRelativeSync(finishedAt, now) {
  const finishedMs = toTimestamp(finishedAt)
  if (!Number.isFinite(finishedMs)) {
    return ''
  }
  const elapsed = now - finishedMs
  if (elapsed < MINUTE_MS) {
    return '刚刚同步'
  }
  if (elapsed < HOUR_MS) {
    return Math.floor(elapsed / MINUTE_MS) + '分钟前同步'
  }
  if (elapsed < DAY_MS) {
    return Math.floor(elapsed / HOUR_MS) + '小时前同步'
  }
  const dayDiff = (ymdUtcMs(shanghaiYmd(now)) - ymdUtcMs(shanghaiYmd(finishedMs))) / DAY_MS
  if (dayDiff === 1) {
    return '昨天同步'
  }
  return dayDiff + '天前同步'
}

export function formatSnapshotFreshness(tradeDate, finishedAt, now = Date.now()) {
  if (isBlank(tradeDate) || isBlank(finishedAt)) {
    return ''
  }
  const dateLabel = formatCloseDateLabel(tradeDate, now)
  const relative = formatRelativeSync(finishedAt, now)
  if (!dateLabel || !relative) {
    return ''
  }
  return '数据截至 ' + dateLabel + '收盘 · ' + relative
}

export function formatUpdatedAt(value) {
  if (isBlank(value)) {
    return ''
  }
  const formatted = parseTime(value)
  if (formatted === null || !UPDATED_AT_PATTERN.test(formatted)) {
    return ''
  }
  return formatted
}
