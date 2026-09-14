'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const variablesPath = path.join(__dirname, '../src/assets/styles/variables.scss')

test('product sidebar width token is 176px', () => {
  const scss = fs.readFileSync(variablesPath, 'utf8')
  const match = scss.match(/\$base-sidebar-width:\s*([^;]+);/)
  assert.ok(match, 'expected $base-sidebar-width in variables.scss')
  assert.equal(match[1].trim(), '176px')
})

test('product sidebar does not hardcode a 股票列表 brand label', () => {
  const sidebarPath = path.join(__dirname, '../src/layout/components/Sidebar/index.vue')
  const source = fs.readFileSync(sidebarPath, 'utf8')
  assert.equal(source.includes('sidebar-brand'), false)
  assert.equal(source.includes('股票列表'), false)
})

test('light sidebar active state is a pill without an edge bar', () => {
  const sidebarScssPath = path.join(__dirname, '../src/assets/styles/sidebar.scss')
  const source = fs.readFileSync(sidebarScssPath, 'utf8')
  assert.equal(source.includes('border-radius: 8px'), true)
  assert.equal(/theme-light[\s\S]*border-right:\s*3px solid/.test(source), false)
})
