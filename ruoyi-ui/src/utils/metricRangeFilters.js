export const METRIC_RANGE_FIELDS = [
  { label: 'PE', minKey: 'peTtmMin', maxKey: 'peTtmMax' },
  { label: 'PB', minKey: 'pbMin', maxKey: 'pbMax' },
  { label: 'ROE', minKey: 'roeMin', maxKey: 'roeMax' },
  { label: '股息率', minKey: 'dvTtmMin', maxKey: 'dvTtmMax' },
  { label: '市值', minKey: 'totalMvYiMin', maxKey: 'totalMvYiMax' }
]

function isBlank(value) {
  if (value === null || value === undefined) {
    return true
  }
  if (typeof value === 'string' && value.trim() === '') {
    return true
  }
  return false
}

function toFiniteNumber(value) {
  if (isBlank(value)) {
    return null
  }
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null
  }
  const cleaned = String(value).trim().replace(/,/g, '').replace(/%/g, '').trim()
  if (cleaned === '') {
    return null
  }
  const n = Number(cleaned)
  return Number.isFinite(n) ? n : null
}

export function hasInvertedRange(params) {
  const src = params || {}
  for (const field of METRIC_RANGE_FIELDS) {
    const min = toFiniteNumber(src[field.minKey])
    const max = toFiniteNumber(src[field.maxKey])
    if (min !== null && max !== null && min > max) {
      return field.label
    }
  }
  return null
}

export function hasInvalidRange(params) {
  const src = params || {}
  for (const field of METRIC_RANGE_FIELDS) {
    for (const key of [field.minKey, field.maxKey]) {
      if (!isBlank(src[key]) && toFiniteNumber(src[key]) === null) {
        return field.label
      }
    }
  }
  return null
}

export function omitBlankRanges(params) {
  const out = { ...(params || {}) }
  for (const field of METRIC_RANGE_FIELDS) {
    for (const key of [field.minKey, field.maxKey]) {
      if (!Object.prototype.hasOwnProperty.call(out, key)) {
        continue
      }
      if (isBlank(out[key])) {
        delete out[key]
        continue
      }
      const n = toFiniteNumber(out[key])
      if (n === null) {
        delete out[key]
      } else {
        out[key] = n
      }
    }
  }
  return out
}

export function pickRangeQuery(routeQuery) {
  const src = routeQuery || {}
  const out = {}
  for (const field of METRIC_RANGE_FIELDS) {
    for (const key of [field.minKey, field.maxKey]) {
      if (!isBlank(src[key])) {
        out[key] = src[key]
      }
    }
  }
  return out
}
