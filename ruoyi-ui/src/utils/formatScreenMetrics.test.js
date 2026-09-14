import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  formatCount,
  formatDecimal,
  formatPercent,
  formatThousands,
  formatTradeDate,
  formatUpdatedAt,
  formatSnapshotFreshness
} from './formatScreenMetrics.js'

test('formatDecimal keeps two places and maps blanks to em dash', () => {
  assert.equal(formatDecimal(1.2), '1.20')
  assert.equal(formatDecimal('4'), '4.00')
  assert.equal(formatDecimal(null), '—')
  assert.equal(formatDecimal(''), '—')
  assert.equal(formatDecimal('abc'), '—')
})

test('formatThousands groups the integer part', () => {
  assert.equal(formatThousands(1234.5), '1,234.50')
  assert.equal(formatThousands(60), '60.00')
  assert.equal(formatThousands(-12000), '-12,000.00')
  assert.equal(formatThousands(undefined), '—')
})

test('formatPercent appends a percent sign', () => {
  assert.equal(formatPercent(4.48), '4.48%')
  assert.equal(formatPercent(null), '—')
})

test('formatTradeDate hyphenates YYYYMMDD', () => {
  assert.equal(formatTradeDate('20260815'), '2026-08-15')
  assert.equal(formatTradeDate('2026-08-15'), '2026-08-15')
  assert.equal(formatTradeDate(''), '')
  assert.equal(formatTradeDate(null), '')
})

test('formatCount truncates to an integer label', () => {
  assert.equal(formatCount(128.9), '128')
  assert.equal(formatCount(0), '0')
  assert.equal(formatCount(null), '—')
})

test('formatUpdatedAt formats ISO and space-separated datetimes', () => {
  assert.equal(formatUpdatedAt('2026-08-19T18:30:05'), '2026-08-19 18:30:05')
  assert.equal(formatUpdatedAt('2026-08-19 18:30:05'), '2026-08-19 18:30:05')
})

test('formatUpdatedAt accepts Date and millisecond timestamps', () => {
  assert.equal(formatUpdatedAt(new Date('2026-08-19T18:30:05')), '2026-08-19 18:30:05')
  assert.equal(formatUpdatedAt(Date.parse('2026-08-19T18:30:05')), '2026-08-19 18:30:05')
})

test('formatUpdatedAt maps blanks and invalid input to empty string', () => {
  assert.equal(formatUpdatedAt(null), '')
  assert.equal(formatUpdatedAt(undefined), '')
  assert.equal(formatUpdatedAt(''), '')
  assert.equal(formatUpdatedAt('not-a-date'), '')
})

const SNAPSHOT_NOW = Date.parse('2026-08-31T20:30:00+08:00')

test('formatSnapshotFreshness shows close date and hours-ago sync', () => {
  assert.equal(
    formatSnapshotFreshness('20260829', '2026-08-31T18:30:00+08:00', SNAPSHOT_NOW),
    '数据截至 8月29日收盘 · 2小时前同步'
  )
})

test('formatSnapshotFreshness treats naive finishedAt as Asia/Shanghai', () => {
  assert.equal(
    formatSnapshotFreshness('20260829', '2026-08-31 18:30:00', SNAPSHOT_NOW),
    '数据截至 8月29日收盘 · 2小时前同步'
  )
  assert.equal(
    formatSnapshotFreshness('20260829', '2026-08-31T18:30:00', SNAPSHOT_NOW),
    '数据截至 8月29日收盘 · 2小时前同步'
  )
})

test('formatSnapshotFreshness includes year when tradeDate is not the current year', () => {
  assert.equal(
    formatSnapshotFreshness('20250829', '2026-08-31T18:30:00+08:00', SNAPSHOT_NOW),
    '数据截至 2025年8月29日收盘 · 2小时前同步'
  )
})

test('formatSnapshotFreshness uses 刚刚同步 within one minute', () => {
  assert.equal(
    formatSnapshotFreshness('20260831', '2026-08-31T20:29:30+08:00', SNAPSHOT_NOW),
    '数据截至 8月31日收盘 · 刚刚同步'
  )
})

test('formatSnapshotFreshness uses minutes within one hour', () => {
  assert.equal(
    formatSnapshotFreshness('20260831', '2026-08-31T20:15:00+08:00', SNAPSHOT_NOW),
    '数据截至 8月31日收盘 · 15分钟前同步'
  )
})

test('formatSnapshotFreshness uses hours within 24 hours even on calendar yesterday', () => {
  assert.equal(
    formatSnapshotFreshness('20260830', '2026-08-30T21:30:00+08:00', SNAPSHOT_NOW),
    '数据截至 8月30日收盘 · 23小时前同步'
  )
})

test('formatSnapshotFreshness uses 昨天同步 for calendar yesterday beyond 24 hours', () => {
  assert.equal(
    formatSnapshotFreshness('20260830', '2026-08-30T19:30:00+08:00', SNAPSHOT_NOW),
    '数据截至 8月30日收盘 · 昨天同步'
  )
})

test('formatSnapshotFreshness uses days for older sync times', () => {
  assert.equal(
    formatSnapshotFreshness('20260829', '2026-08-29T18:30:00+08:00', SNAPSHOT_NOW),
    '数据截至 8月29日收盘 · 2天前同步'
  )
})

test('formatSnapshotFreshness maps missing tradeDate or finishedAt to empty string', () => {
  assert.equal(formatSnapshotFreshness(null, '2026-08-31T18:30:00+08:00', SNAPSHOT_NOW), '')
  assert.equal(formatSnapshotFreshness('20260829', null, SNAPSHOT_NOW), '')
  assert.equal(formatSnapshotFreshness(undefined, '2026-08-31T18:30:00+08:00', SNAPSHOT_NOW), '')
  assert.equal(formatSnapshotFreshness('20260829', undefined, SNAPSHOT_NOW), '')
  assert.equal(formatSnapshotFreshness('', '2026-08-31T18:30:00+08:00', SNAPSHOT_NOW), '')
  assert.equal(formatSnapshotFreshness('20260829', '', SNAPSHOT_NOW), '')
})
