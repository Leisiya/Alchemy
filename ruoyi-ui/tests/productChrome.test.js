'use strict'

const { test } = require('node:test')
const assert = require('node:assert/strict')
const {
  dropdownPlacementFor,
  PRODUCT_THEME,
  LAYOUT_SETTING_KEY,
  clearStoredLayoutSetting,
  resolveProductTheme,
  sidebarCollapseLabel
} = require('../src/utils/productChrome')

test('sidebar avatar menu opens top-start', () => {
  assert.equal(dropdownPlacementFor('sidebar'), 'top-start')
})

test('navbar avatar menu opens bottom-end', () => {
  assert.equal(dropdownPlacementFor('navbar'), 'bottom-end')
})

test('product theme is locked to #15803D', () => {
  assert.equal(PRODUCT_THEME, '#15803D')
  assert.equal(resolveProductTheme('#409EFF'), '#15803D')
  assert.equal(resolveProductTheme('#11a983'), '#15803D')
})

test('sidebar collapse toggle label follows opened state', () => {
  assert.equal(sidebarCollapseLabel(true), '收起侧栏')
  assert.equal(sidebarCollapseLabel(false), '展开侧栏')
})

test('clearStoredLayoutSetting removes layout-setting', () => {
  const storage = {
    data: { 'layout-setting': '{"theme":"#409EFF"}' },
    removeItem(key) {
      delete this.data[key]
    }
  }
  clearStoredLayoutSetting(storage)
  assert.equal(storage.data[LAYOUT_SETTING_KEY], undefined)
})
