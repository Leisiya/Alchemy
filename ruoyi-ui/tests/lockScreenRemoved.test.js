'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const uiRoot = path.join(__dirname, '..')
const repoRoot = path.join(__dirname, '../..')

function read(rel) {
  return fs.readFileSync(path.join(uiRoot, rel), 'utf8')
}

test('lock vuex module file is gone', () => {
  assert.equal(fs.existsSync(path.join(uiRoot, 'src/store/modules/lock.js')), false)
})

test('lock view file is gone', () => {
  assert.equal(fs.existsSync(path.join(uiRoot, 'src/views/lock.vue')), false)
})

test('router has no /lock route', () => {
  assert.doesNotMatch(read('src/router/index.js'), /path:\s*'\/lock'/)
})

test('permission gate does not use isLock', () => {
  assert.doesNotMatch(read('src/permission.js'), /isLock/)
})

test('login api does not expose unlockScreen', () => {
  assert.doesNotMatch(read('src/api/login.js'), /unlockScreen|unlockscreen/)
})

test('user login does not dispatch lock unlock', () => {
  assert.doesNotMatch(read('src/store/modules/user.js'), /lock\/unlockScreen/)
})

test('vuex store does not register lock', () => {
  assert.doesNotMatch(read('src/store/index.js'), /lock/)
})

test('getters do not expose lock state', () => {
  const getters = read('src/store/getters.js')
  assert.doesNotMatch(getters, /isLock/)
  assert.doesNotMatch(getters, /lockPath/)
})

test('avatar menu has no lock command', () => {
  assert.doesNotMatch(read('src/layout/components/Sidebar/SidebarUser.vue'), /command="lock"|锁定屏幕|lockScreen/)
})

test('backend unlockscreen endpoint is gone', () => {
  const controller = fs.readFileSync(
    path.join(repoRoot, 'ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysIndexController.java'),
    'utf8'
  )
  assert.doesNotMatch(controller, /unlockscreen|unlockScreen/)
})
