'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const root = path.join(__dirname, '..')
const routerPath = path.join(root, 'src/router/index.js')

test('router keeps 我的自选 and has no 关于作者 or 社区', () => {
  const source = fs.readFileSync(routerPath, 'utf8')
  assert.equal(source.includes("path: '/stock/watchlist'"), true)
  assert.equal(source.includes("path: '/about'"), false)
  assert.equal(source.includes("path: '/community'"), false)
  assert.equal(source.includes("title: '关于作者'"), false)
  assert.equal(source.includes("title: '社区'"), false)
  assert.equal(source.includes('SiteAbout'), false)
  assert.equal(source.includes("icon: 'education'"), false)
  assert.equal(source.includes('@/views/site/about'), false)
  assert.equal(source.includes('@/views/site/community'), false)
})

test('about page, author utils, resume, and visual spec are gone', () => {
  assert.equal(fs.existsSync(path.join(root, 'src/views/site/about/index.vue')), false)
  assert.equal(fs.existsSync(path.join(root, 'src/utils/authorCommunity.js')), false)
  assert.equal(fs.existsSync(path.join(root, 'src/utils/authorResumeDownload.js')), false)
  assert.equal(fs.existsSync(path.join(root, 'public/author/resume.pdf')), false)
  assert.equal(
    fs.existsSync(path.join(root, '..', 'docs/agent/alchemy/design/pages/about.md')),
    false
  )
})

test('community page files and QR images are gone', () => {
  assert.equal(fs.existsSync(path.join(root, 'src/views/site/community/index.vue')), false)
  assert.equal(fs.existsSync(path.join(root, 'public/community/qq-qr.png')), false)
  assert.equal(fs.existsSync(path.join(root, 'public/community/wechat-qr.png')), false)
})
