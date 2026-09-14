'use strict'

const { test } = require('node:test')
const assert = require('node:assert/strict')
const {
  LOCAL_KEY,
  SESSION_KEY,
  shortcutHint,
  shouldShowBookmarkTip,
  readDismissed,
  persistDismiss
} = require('./bookmarkTip')

test('Mac userAgent returns ⌘ + D shortcut hint', () => {
  assert.equal(
    shortcutHint('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'MacIntel'),
    '⌘ + D'
  )
})

test('Windows userAgent returns Ctrl + D shortcut hint', () => {
  assert.equal(
    shortcutHint('Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Win32'),
    'Ctrl + D'
  )
})

test('shouldShowBookmarkTip is false when dismissedForever', () => {
  assert.equal(
    shouldShowBookmarkTip({
      dismissedForever: true,
      dismissedSession: false,
      device: 'desktop'
    }),
    false
  )
})

test('shouldShowBookmarkTip is false when dismissedSession', () => {
  assert.equal(
    shouldShowBookmarkTip({
      dismissedForever: false,
      dismissedSession: true,
      device: 'desktop'
    }),
    false
  )
})

test('shouldShowBookmarkTip is false on mobile', () => {
  assert.equal(
    shouldShowBookmarkTip({
      dismissedForever: false,
      dismissedSession: false,
      device: 'mobile'
    }),
    false
  )
})

test('shouldShowBookmarkTip is true on desktop when not dismissed', () => {
  assert.equal(
    shouldShowBookmarkTip({
      dismissedForever: false,
      dismissedSession: false,
      device: 'desktop'
    }),
    true
  )
})

test('persistDismiss with dontShowAgain writes LOCAL_KEY on localStore', () => {
  const localStore = { data: {}, set(key, value) { this.data[key] = value } }
  const sessionStore = { data: {}, set(key, value) { this.data[key] = value } }

  persistDismiss({ dontShowAgain: true, localStore, sessionStore })

  assert.equal(localStore.data[LOCAL_KEY], '1')
  assert.equal(sessionStore.data[SESSION_KEY], undefined)
})

test('persistDismiss without dontShowAgain writes SESSION_KEY on sessionStore', () => {
  const localStore = { data: {}, set(key, value) { this.data[key] = value } }
  const sessionStore = { data: {}, set(key, value) { this.data[key] = value } }

  persistDismiss({ dontShowAgain: false, localStore, sessionStore })

  assert.equal(sessionStore.data[SESSION_KEY], '1')
  assert.equal(localStore.data[LOCAL_KEY], undefined)
})

test('readDismissed maps stored flags correctly', () => {
  const localStore = {
    data: { [LOCAL_KEY]: '1' },
    get(key) { return this.data[key] }
  }
  const sessionStore = {
    data: { [SESSION_KEY]: '1' },
    get(key) { return this.data[key] }
  }

  assert.deepEqual(readDismissed(localStore, sessionStore), {
    dismissedForever: true,
    dismissedSession: true
  })

  const emptyLocal = { data: {}, get(key) { return this.data[key] } }
  const emptySession = { data: {}, get(key) { return this.data[key] } }

  assert.deepEqual(readDismissed(emptyLocal, emptySession), {
    dismissedForever: false,
    dismissedSession: false
  })
})
