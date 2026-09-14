'use strict'

const LAYOUT_SETTING_KEY = 'layout-setting'
const PRODUCT_THEME = '#15803D'

function dropdownPlacementFor(chromePlacement) {
  return chromePlacement === 'navbar' ? 'bottom-end' : 'top-start'
}

function resolveProductTheme() {
  return PRODUCT_THEME
}

function clearStoredLayoutSetting(storage) {
  if (storage && typeof storage.removeItem === 'function') {
    storage.removeItem(LAYOUT_SETTING_KEY)
  }
}

function sidebarCollapseLabel(opened) {
  return opened ? '收起侧栏' : '展开侧栏'
}

module.exports = {
  LAYOUT_SETTING_KEY,
  PRODUCT_THEME,
  dropdownPlacementFor,
  resolveProductTheme,
  clearStoredLayoutSetting,
  sidebarCollapseLabel
}
