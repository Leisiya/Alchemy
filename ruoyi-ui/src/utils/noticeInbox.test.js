'use strict'

const { test } = require('node:test')
const assert = require('node:assert/strict')
const {
  STORAGE_KEY,
  unreadBadgeLabel,
  stripHtmlPreview,
  parseGuestReadIds,
  applyGuestReadOverlay,
  guestUnreadCount,
  appendGuestReadId,
  appendAllGuestReadIds,
  relativeTime
} = require('./noticeInbox')

test('storage key is alchemy.noticeRead.ids', () => {
  assert.equal(STORAGE_KEY, 'alchemy.noticeRead.ids')
})

test('unread badge label is semantic, not a bare number', () => {
  assert.equal(unreadBadgeLabel(0), '通知中心')
  assert.equal(unreadBadgeLabel(3), '通知中心，3 条未读')
})

test('stripHtmlPreview drops tags and truncates', () => {
  assert.equal(stripHtmlPreview('<p>hello <b>world</b></p>', 8), 'hello wo…')
})

test('guest overlay marks stored ids read', () => {
  const rows = applyGuestReadOverlay(
    [{ noticeId: 1, isRead: false }, { noticeId: 2, isRead: false }],
    [1]
  )
  assert.equal(rows[0].isRead, true)
  assert.equal(rows[1].isRead, false)
  assert.equal(guestUnreadCount(rows, [1]), 1)
})

test('parseGuestReadIds ignores junk', () => {
  assert.deepEqual(parseGuestReadIds('not-json'), [])
  assert.deepEqual(parseGuestReadIds('[1,2]'), [1, 2])
})

test('appendGuestReadId is idempotent', () => {
  assert.equal(appendGuestReadId('[1]', 1), '[1]')
  assert.equal(appendGuestReadId('[]', 9), '[9]')
})

test('appendGuestReadId coerces numeric strings and drops junk', () => {
  assert.equal(appendGuestReadId('[]', '9'), '[9]')
  assert.equal(appendGuestReadId('[1]', 0), '[1]')
  assert.equal(appendGuestReadId('[1]', -3), '[1]')
  assert.equal(appendGuestReadId('[1]', 'junk'), '[1]')
  assert.equal(appendGuestReadId('[1]', NaN), '[1]')
})

test('appendGuestReadId rejects boolean and non-numeric types', () => {
  assert.equal(appendGuestReadId('[]', true), '[]')
  assert.equal(appendGuestReadId('[]', false), '[]')
  assert.equal(appendGuestReadId('[]', ''), '[]')
  assert.equal(appendGuestReadId('[1]', null), '[1]')
  assert.equal(appendGuestReadId('[1]', undefined), '[1]')
})

test('appendGuestReadId compacts duplicate ids in raw', () => {
  assert.equal(appendGuestReadId('[1,1]', 2), '[1,2]')
  assert.equal(appendGuestReadId('[1,1]', 1), '[1]')
})

test('appendAllGuestReadIds unions ids', () => {
  assert.equal(appendAllGuestReadIds('[1]', [1, 2]), '[1,2]')
})

test('appendAllGuestReadIds coerces, dedupes, and compacts raw duplicates', () => {
  assert.equal(appendAllGuestReadIds('[1,1]', [1, 2, '3', 0, -1, 'junk']), '[1,2,3]')
  assert.equal(appendAllGuestReadIds('[2,1]', ['9', 2]), '[2,1,9]')
})

test('appendAllGuestReadIds rejects arrays objects and booleans', () => {
  assert.equal(appendAllGuestReadIds('[]', [[9]]), '[]')
  assert.equal(appendAllGuestReadIds('[]', [{ noticeId: 9 }]), '[]')
  assert.equal(appendAllGuestReadIds('[1]', [true, false, '']), '[1]')
})

test('relativeTime uses Chinese buckets', () => {
  const now = Date.parse('2026-08-29T12:00:00+08:00')
  assert.equal(relativeTime(new Date(now - 10 * 1000), now), '刚刚')
  assert.equal(relativeTime(new Date(now - 5 * 60 * 1000), now), '5分钟前')
  assert.equal(relativeTime(new Date(now - 3 * 60 * 60 * 1000), now), '3小时前')
  assert.equal(relativeTime(new Date(now - 26 * 60 * 60 * 1000), now), '昨天')
  assert.equal(relativeTime(new Date('2026-08-01T08:00:00+08:00'), now), '2026-08-01')
})
