'use strict'

const STORAGE_KEY = 'alchemy.noticeRead.ids'
const INBOX_LIMIT = 50
const POLL_MS = 60000

function unreadBadgeLabel(count) {
  if (!count) {
    return '通知中心'
  }
  return `通知中心，${count} 条未读`
}

function stripHtmlPreview(html, maxLen = 80) {
  if (!html) {
    return ''
  }
  const text = html
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim()
  if (text.length <= maxLen) {
    return text
  }
  return text.slice(0, maxLen) + '…'
}

function parseGuestReadIdsArray(raw) {
  if (!raw) {
    return []
  }
  try {
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function normalizeGuestReadIds(ids) {
  const seen = new Set()
  const result = []
  for (const id of ids) {
    if (typeof id !== 'number' && (typeof id !== 'string' || id === '')) {
      continue
    }
    const n = Number(id)
    if (Number.isFinite(n) && n > 0 && !seen.has(n)) {
      seen.add(n)
      result.push(n)
    }
  }
  return result
}

function parseGuestReadIds(raw) {
  if (!raw) {
    return []
  }
  try {
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) {
      return []
    }
    return parsed.filter((id) => typeof id === 'number' && Number.isFinite(id))
  } catch {
    return []
  }
}

function applyGuestReadOverlay(notices, readIds) {
  const readSet = new Set(readIds)
  return notices.map((notice) => ({
    ...notice,
    isRead: notice.isRead || readSet.has(notice.noticeId)
  }))
}

function guestUnreadCount(notices, readIds) {
  const readSet = new Set(readIds)
  return notices.filter((notice) => !(notice.isRead || readSet.has(notice.noticeId))).length
}

function appendGuestReadId(raw, noticeId) {
  const ids = normalizeGuestReadIds([...parseGuestReadIdsArray(raw || '[]'), noticeId])
  return JSON.stringify(ids)
}

function appendAllGuestReadIds(raw, noticeIds) {
  const ids = normalizeGuestReadIds([...parseGuestReadIdsArray(raw || '[]'), ...noticeIds])
  return JSON.stringify(ids)
}

function startOfDay(date) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  return d
}

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function calendarDayDiff(from, to) {
  const msPerDay = 24 * 60 * 60 * 1000
  return Math.round((startOfDay(to) - startOfDay(from)) / msPerDay)
}

function relativeTime(date, now) {
  const d = date instanceof Date ? date : new Date(date)
  const n = now instanceof Date ? now : new Date(now)
  const diffMs = n - d

  if (diffMs < 60 * 1000) {
    return '刚刚'
  }
  if (diffMs < 60 * 60 * 1000) {
    return `${Math.floor(diffMs / (60 * 1000))}分钟前`
  }
  if (diffMs < 24 * 60 * 60 * 1000) {
    return `${Math.floor(diffMs / (60 * 60 * 1000))}小时前`
  }
  if (calendarDayDiff(d, n) === 1) {
    return '昨天'
  }
  return formatDate(d)
}

module.exports = {
  STORAGE_KEY,
  INBOX_LIMIT,
  POLL_MS,
  unreadBadgeLabel,
  stripHtmlPreview,
  parseGuestReadIds,
  applyGuestReadOverlay,
  guestUnreadCount,
  appendGuestReadId,
  appendAllGuestReadIds,
  relativeTime
}
