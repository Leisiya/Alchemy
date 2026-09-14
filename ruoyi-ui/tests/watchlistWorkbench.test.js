'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const routerPath = path.join(__dirname, '../src/router/index.js')
const screenerPath = path.join(__dirname, '../src/views/stock/screener/index.vue')
const apiPath = path.join(__dirname, '../src/api/stock/watchlist.js')

test('router exposes 我的自选 as a constant sibling of signal menus', () => {
  const source = fs.readFileSync(routerPath, 'utf8')
  assert.equal(source.includes("path: '/stock/watchlist'"), true)
  assert.equal(source.includes("title: '我的自选'"), true)
  assert.match(source, /path: '\/stock\/watchlist'[\s\S]*?icon: 'star'/)
  assert.match(source, /path: '\/stock\/breakout'[\s\S]*?icon: 'guide'/)
  assert.equal(source.includes("icon: 'clipboard'"), false)
  assert.equal(source.includes('watchlist: true'), true)
  assert.equal(source.includes("signal: '破位低估'"), true)
  assert.equal(source.includes("signal: '强势突破'"), true)
})

test('screener stars rows and branches watchlist empty copy', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')
  assert.equal(source.includes('el-icon-star-on'), true)
  assert.equal(source.includes('el-icon-star-off'), true)
  assert.equal(source.includes('已不在候选池'), true)
  assert.equal(source.includes('还没有自选股票，可在股票列表中点击星标加入。'), true)
  assert.equal(source.includes('listWatchlist'), true)
  assert.equal(source.includes('v-if="!isWatchlistPage"'), true)
  assert.equal(source.includes('if (this.isGuest)'), true)
})

test('watchlist loads rows when the dashboard request fails', () => {
  const source = fs.readFileSync(screenerPath, 'utf8')
  const initializePage = source.slice(source.indexOf('initializePage() {'), source.indexOf('\n    getList() {'))

  assert.match(
    initializePage,
    /\.catch\(\(\) => \{\s*if \(this\.isWatchlistPage\) \{\s*this\.getList\(\)\s*return\s*\}\s*this\.setListLoading\(false\)/
  )
})

test('watchlist api covers list codes add and remove', () => {
  const source = fs.readFileSync(apiPath, 'utf8')
  assert.equal(source.includes('/stock/watchlist/list'), true)
  assert.equal(source.includes('/stock/watchlist/codes'), true)
  assert.equal(source.includes("url: '/stock/watchlist'"), true)
  assert.equal(source.includes("method: 'delete'"), true)
})
