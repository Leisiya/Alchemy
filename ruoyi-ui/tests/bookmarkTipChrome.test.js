'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const uiRoot = path.join(__dirname, '..')

function read(rel) {
  const file = path.join(uiRoot, rel)
  return fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : ''
}

test('layout renders the bookmark tip from the component barrel', () => {
  const layout = read('src/layout/index.vue')
  const barrel = read('src/layout/components/index.js')

  assert.match(layout, /import\s*\{[^}]*BookmarkTip[^}]*\}\s*from\s*['"]\.\/components['"]/)
  assert.match(layout, /<bookmark-tip\s*\/?>/)
  assert.match(barrel, /export\s*\{\s*default\s+as\s+BookmarkTip\s*\}\s*from\s*['"]\.\/BookmarkTip['"]/)
})

test('bookmark tip keeps the required accessible product chrome', () => {
  const tip = read('src/layout/components/BookmarkTip/index.vue')

  assert.match(tip, /aria-label="关闭收藏提示"/)
  assert.match(tip, /收藏本站/)
  assert.match(tip, /不再提示/)
  assert.match(tip, /知道了/)
  assert.match(tip, /#F59E0B/)
  assert.match(tip, /z-index:\s*1002/)
  assert.match(tip, /prefers-reduced-motion/)
  assert.doesNotMatch(tip, /phosphor/i)
  assert.ok(
    tip.indexOf('class="bookmark-tip__close"') < tip.indexOf('知道了'),
    'close button should precede the confirm action in DOM order'
  )
})

test('mobile resize pauses rather than dismisses the bookmark tip', () => {
  const tip = read('src/layout/components/BookmarkTip/index.vue')
  const watcher = tip.slice(tip.indexOf('watch:'), tip.indexOf('created()'))

  assert.doesNotMatch(watcher, /this\.visible\s*=\s*false/)
  assert.match(watcher, /this\.clearShowTimer\(\)/)
  assert.match(watcher, /this\.scheduleShow\(\)/)
  assert.match(tip, /created\(\)\s*\{\s*this\.scheduleShow\(\)\s*\}/)
  assert.match(tip, /scheduleShow\(\)\s*\{[\s\S]*shouldShowBookmarkTip/)
})
