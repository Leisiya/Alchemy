'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const uiRoot = path.join(__dirname, '..')

function read(rel) {
  return fs.readFileSync(path.join(uiRoot, rel), 'utf8')
}

test('settings drawer component is gone', () => {
  assert.equal(fs.existsSync(path.join(uiRoot, 'src/layout/components/Settings/index.vue')), false)
})

test('layout barrel does not export Settings', () => {
  assert.doesNotMatch(read('src/layout/components/index.js'), /Settings/)
})

test('avatar menu has no layout settings item', () => {
  const src = read('src/layout/components/Sidebar/SidebarUser.vue')
  assert.doesNotMatch(src, /布局设置|command="layout"|setLayout|showSettings/)
})

test('shell no longer opens layout settings', () => {
  assert.doesNotMatch(read('src/layout/index.vue'), /setLayout|settingRef|Settings/)
  assert.doesNotMatch(read('src/layout/components/Navbar.vue'), /setLayout/)
  assert.doesNotMatch(read('src/layout/components/Sidebar/index.vue'), /setLayout/)
})

test('product chrome defaults are frozen', () => {
  const settings = require('../src/settings')
  assert.equal(settings.showSettings, false)
  assert.equal(settings.dynamicTitle, true)
  assert.equal(settings.sideTheme, 'theme-light')
  assert.equal(settings.navType, 1)
  assert.equal(settings.fixedHeader, true)
  assert.equal(settings.sidebarLogo, true)
  assert.equal(settings.footerVisible, false)
  assert.equal(settings.tagsView, false)
})

test('vuex settings ignore layout-setting storage', () => {
  const src = read('src/store/modules/settings.js')
  assert.doesNotMatch(src, /readLayoutSetting|LEGACY_THEMES/)
  assert.match(src, /clearStoredLayoutSetting/)
  assert.match(src, /PRODUCT_THEME/)
})
