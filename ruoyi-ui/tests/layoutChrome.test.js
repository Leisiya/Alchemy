'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const sidebarUserPath = path.join(__dirname, '../src/layout/components/Sidebar/SidebarUser.vue')
const sidebarCollapseTogglePath = path.join(
  __dirname,
  '../src/layout/components/Sidebar/SidebarCollapseToggle.vue'
)

test('SidebarCollapseToggle imports productChrome as default export', () => {
  const source = fs.readFileSync(sidebarCollapseTogglePath, 'utf8')
  assert.equal(source.includes("import productChrome from '@/utils/productChrome'"), true)
  assert.equal(source.includes('import { sidebarCollapseLabel'), false)
})

test('logout does not confirm before LogOut', () => {
  const source = fs.readFileSync(sidebarUserPath, 'utf8')
  assert.equal(source.includes("确定注销并退出系统吗？"), false)
  assert.equal(source.includes("$confirm"), false)
  assert.equal(source.includes("dispatch('LogOut')"), true)
  assert.equal(source.includes("location.href = '/index'"), true)
})
