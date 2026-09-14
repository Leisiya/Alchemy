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

function assertNoPhosphor(source, label) {
  assert.doesNotMatch(source, /@phosphor-icons/, `${label} must not import phosphor`)
}

test('sidebar mounts notice-center-entry before sidebar-user', () => {
  const sidebar = read('src/layout/components/Sidebar/index.vue')
  assert.match(sidebar, /notice-center-entry/)
  const entryIdx = sidebar.indexOf('notice-center-entry')
  const userIdx = sidebar.indexOf('sidebar-user')
  assert.ok(
    entryIdx >= 0 && userIdx >= 0 && entryIdx < userIdx,
    'notice-center-entry should appear before sidebar-user'
  )
  assertNoPhosphor(sidebar, 'Sidebar')
})

test('NoticeCenterEntry uses bell badge and unreadBadgeLabel', () => {
  const entry = read('src/layout/components/NoticeCenterEntry.vue')
  assert.match(entry, /icon-class="bell"/)
  assert.match(entry, /el-badge/)
  assert.match(entry, /unreadBadgeLabel/)
  assert.match(entry, /aria-expanded/)
  assertNoPhosphor(entry, 'NoticeCenterEntry')
})

test('NoticeDrawer is a 400px rtl drawer with empty and mark-all chrome', () => {
  const drawer = read('src/layout/components/NoticeDrawer.vue')
  assert.match(drawer, /el-drawer/)
  assert.match(drawer, /:size="drawerSize"/)
  assert.match(drawer, /'400px'/)
  assert.match(drawer, /'100%'/)
  assert.match(drawer, /暂无通知/)
  assert.match(drawer, /全部已读/)
  assert.match(drawer, /direction="rtl"/)
  assert.match(drawer, /v-html/)
  assert.match(drawer, /加载失败/)
  assert.match(drawer, /--color-foreground/)
  assert.match(drawer, /--color-muted-foreground/)
  assert.match(drawer, /--radius-md/)
  assertNoPhosphor(drawer, 'NoticeDrawer')
})

test('navbar mounts notice-center-entry for mobile chrome', () => {
  const navbar = read('src/layout/components/Navbar.vue')
  assert.match(navbar, /notice-center-entry/)
  assertNoPhosphor(navbar, 'Navbar')
})

test('navbar notice entry keeps horizontal padding and visible badge overflow', () => {
  const entry = read('src/layout/components/NoticeCenterEntry.vue')
  const navbar = read('src/layout/components/Navbar.vue')
  assert.match(
    entry,
    /\.notice-center-entry--navbar\.is-collapse\s*\{[^}]*padding:\s*0\s+\d+px/
  )
  assert.doesNotMatch(
    entry,
    /\.notice-center-entry--navbar\.is-collapse\s*\{[^}]*padding:\s*8px\s+0/
  )
  assert.match(
    entry,
    /\.notice-center-entry--navbar(?:\.is-collapse)?\s*\{[^}]*overflow:\s*visible/
  )
  assert.match(navbar, /\.navbar\s*\{[^}]*overflow:\s*visible/)
})

test('layout mounts notice-drawer and polls unread', () => {
  const layout = read('src/layout/index.vue')
  assert.match(layout, /notice-drawer/)
  assert.match(layout, /POLL_MS|60000/)
  assert.match(layout, /beforeDestroy/)
  assertNoPhosphor(layout, 'Layout')
})

test('notice api exposes inbox and admin endpoints', () => {
  const api = read('src/api/system/notice.js')
  assert.match(api, /export function listInbox/)
  assert.match(api, /\/system\/notice\/inbox/)
  assert.match(api, /export function getNoticeUnreadCount/)
  assert.match(api, /\/system\/notice\/unread-count/)
  assert.match(api, /export function markNoticeRead/)
  assert.match(api, /\/system\/notice\/read\//)
  assert.match(api, /export function markNoticeReadAll/)
  assert.match(api, /\/system\/notice\/read-all/)
  assert.match(api, /export function listNotice/)
  assert.match(api, /export function getNotice/)
  assert.match(api, /export function addNotice/)
  assert.match(api, /export function updateNotice/)
  assert.match(api, /export function delNotice/)
})

test('vuex notice module is namespaced with inbox actions', () => {
  const store = read('src/store/modules/notice.js')
  const index = read('src/store/index.js')
  assert.match(store, /namespaced:\s*true/)
  assert.match(store, /unreadCount/)
  assert.match(store, /drawerVisible/)
  assert.match(store, /activeId/)
  assert.match(store, /fetchUnread/)
  assert.match(store, /openDrawer/)
  assert.match(store, /closeDrawer/)
  assert.match(store, /openItem/)
  assert.match(store, /markAll/)
  assert.match(store, /guestUnreadCount/)
  assert.match(store, /STORAGE_KEY/)
  assert.match(index, /from\s+['"]\.\/modules\/notice['"]/)
})

test('mark-read failures do not set inbox list error', () => {
  const store = read('src/store/modules/notice.js')
  const openDrawer = store.slice(store.indexOf('openDrawer'), store.indexOf('closeDrawer'))
  const openItem = store.slice(store.indexOf('openItem'), store.indexOf('markAll'))
  const markAll = store.slice(store.indexOf('markAll'))
  assert.match(openDrawer, /commit\('SET_ERROR'/)
  assert.doesNotMatch(openItem, /SET_ERROR/)
  assert.doesNotMatch(markAll, /SET_ERROR/)
})
