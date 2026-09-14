'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const src = fs.readFileSync(path.join(__dirname, '../public/index.html'), 'utf8')

function cssBlock(selectorPattern) {
  const match = src.match(new RegExp(selectorPattern + '\\s*\\{([^}]*)\\}'))
  return match ? match[1] : ''
}

test('first-paint splash uses auth navy instead of RuoYi purple', () => {
  assert.match(src, /#0D1B2A/)
  assert.match(src, /#15803D/)
  assert.doesNotMatch(src, /#7171C6|#7b78c4|loader-wrapper/i)
})

test('navy stays on .app-splash and does not paint html/body/#app', () => {
  const globalBlock = cssBlock('html\\s*,\\s*body\\s*,\\s*#app')
  assert.notEqual(globalBlock, '')
  assert.doesNotMatch(globalBlock, /background/)
  const splashBlock = cssBlock('\\.app-splash')
  assert.match(splashBlock, /#0D1B2A/)
})

test('splash shows product brand and a short status', () => {
  assert.match(src, /app-splash__brand/)
  assert.match(src, />Alchemy</)
  assert.match(src, /A股价值投资好助手/)
  assert.match(src, /正在加载/)
  assert.doesNotMatch(src, /正在加载系统资源，请耐心等待/)
})

test('splash exposes busy status and honors reduced motion', () => {
  assert.match(src, /role="status"/)
  assert.match(src, /aria-busy="true"/)
  assert.match(src, /prefers-reduced-motion:\s*reduce/)
  assert.match(src, /PingFang SC/)
  assert.doesNotMatch(src, /Open Sans/)
})
