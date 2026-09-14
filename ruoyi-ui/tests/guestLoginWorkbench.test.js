'use strict'
const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

test('login api exposes guestLogin without token', () => {
  const source = fs.readFileSync(path.join(__dirname, '../src/api/login.js'), 'utf8')
  assert.equal(source.includes("url: '/login/guest'"), true)
  assert.equal(source.includes('export function guestLogin'), true)
  assert.equal(source.includes('isToken: false'), true)
})

test('login view has secondary 访客体验 button', () => {
  const source = fs.readFileSync(path.join(__dirname, '../src/views/login.vue'), 'utf8')
  assert.equal(source.includes('访客体验'), true)
  assert.equal(source.includes('handleGuestLogin'), true)
  assert.equal(source.includes('guestEnabled'), true)
  assert.equal(source.includes('type="button"'), true)
  assert.equal(source.includes('auth-guest-btn'), true)
  assert.equal(source.includes('返回首页'), false)
})

test('vuex stores isGuest from getInfo', () => {
  const source = fs.readFileSync(path.join(__dirname, '../src/store/modules/user.js'), 'utf8')
  assert.equal(source.includes('isGuest: false'), true)
  assert.equal(source.includes('SET_IS_GUEST'), true)
  assert.equal(source.includes('res.isGuest === true'), true)
  assert.equal(source.includes('GuestLogin'), true)
})

test('guest banner copy and sessionStorage key', () => {
  const source = fs.readFileSync(path.join(__dirname, '../src/layout/components/GuestBanner/index.vue'), 'utf8')
  assert.equal(source.includes('欢迎访客！您可以体验基本功能。'), true)
  assert.equal(source.includes('注册后解锁自选'), true)
  assert.equal(source.includes('alchemy.guestBanner.dismissed'), true)
  assert.equal(source.includes('aria-label="关闭访客提示"'), true)
  assert.equal(source.includes('最多 3'), false)
})

test('sidebar guest menu registers instead of profile', () => {
  const source = fs.readFileSync(path.join(__dirname, '../src/layout/components/Sidebar/SidebarUser.vue'), 'utf8')
  assert.equal(source.includes('isGuest'), true)
  assert.equal(source.includes('立即注册'), true)
})

test('permission redirects guest profile to register', () => {
  const source = fs.readFileSync(path.join(__dirname, '../src/permission.js'), 'utf8')
  assert.equal(source.includes("/user/profile"), true)
  assert.equal(source.includes('isGuest'), true)
  assert.equal(source.includes('/register'), true)
})

test('screener guest skips watchlist apis and shows lock copy', () => {
  const screener = fs.readFileSync(path.join(__dirname, '../src/views/stock/screener/index.vue'), 'utf8')
  const lock = fs.readFileSync(path.join(__dirname, '../src/views/stock/screener/GuestWatchlistLock.vue'), 'utf8')
  assert.equal(screener.includes('GuestWatchlistLock'), true)
  assert.equal(screener.includes('isGuest && isWatchlistPage'), true)
  assert.equal(screener.includes('openGuestWatchlistLock'), false)
  assert.equal(screener.includes('guestLockVisible'), false)
  assert.equal(screener.includes("msgWarning('自选功能需要注册')"), true)
  assert.equal(lock.includes('el-dialog'), false)
  assert.equal(lock.includes('append-to-body'), false)
  assert.equal(lock.includes('show-close'), false)
  assert.equal(lock.includes('自选功能需要注册'), true)
  assert.equal(lock.includes('立即注册完整账号'), true)
  assert.equal(lock.includes('云端保存自选'), true)
})
