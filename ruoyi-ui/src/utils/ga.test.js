import { test } from 'node:test'
import assert from 'node:assert/strict'
import { shouldTrackGa, buildPageviewPayload, trackPageview } from './ga.js'

test('shouldTrackGa is false for empty ids', () => {
  assert.equal(shouldTrackGa(''), false)
  assert.equal(shouldTrackGa('   '), false)
  assert.equal(shouldTrackGa(undefined), false)
})

test('shouldTrackGa is true for a GA4 measurement id', () => {
  assert.equal(shouldTrackGa('G-ABCDEF1234'), true)
})

test('buildPageviewPayload fills defaults', () => {
  assert.deepEqual(buildPageviewPayload(), { page_path: '/', page_title: '' })
  assert.deepEqual(buildPageviewPayload('/screener', '筛股'), {
    page_path: '/screener',
    page_title: '筛股'
  })
})

test('trackPageview no-ops without a gtag function', () => {
  assert.equal(trackPageview('/login', '登录', { measurementId: 'G-TEST' }), false)
})

test('trackPageview sends page_view when gtag is provided', () => {
  const calls = []
  const sent = trackPageview('/screener', '筛股', {
    measurementId: 'G-TEST',
    gtag: (...args) => { calls.push(args) }
  })
  assert.equal(sent, true)
  assert.deepEqual(calls, [[
    'event',
    'page_view',
    { page_path: '/screener', page_title: '筛股' }
  ]])
})
