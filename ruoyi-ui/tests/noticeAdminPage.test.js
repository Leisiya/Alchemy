'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const uiRoot = path.join(__dirname, '..')
const pageRel = 'src/views/system/notice/index.vue'

function read(rel) {
  const file = path.join(uiRoot, rel)
  return fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : ''
}

test('admin notice page uses Editor, dicts, and add permission', () => {
  const page = read(pageRel)
  assert.notEqual(page, '', `${pageRel} must exist`)
  assert.match(page, /<editor\b/i)
  assert.match(page, /v-model="form\.noticeContent"/)
  assert.match(page, /:min-height="192"/)
  assert.match(page, /noticeTitle/)
  assert.match(page, /v-hasPermi="\['system:notice:add'\]"/)
  assert.match(page, /sys_notice_type/)
  assert.match(page, /sys_notice_status/)
  assert.match(page, /dicts:\s*\[\s*['"]sys_notice_status['"]\s*,\s*['"]sys_notice_type['"]\s*\]/)
})

test('admin notice page is RuoYi CRUD with type tag and edit/remove perms', () => {
  const page = read(pageRel)
  assert.match(page, /dict-tag/)
  assert.match(page, /v-hasPermi="\['system:notice:edit'\]"/)
  assert.match(page, /v-hasPermi="\['system:notice:remove'\]"/)
  assert.match(page, /maxlength="50"/)
  assert.match(page, /from\s+['"]@\/api\/system\/notice['"]/)
  assert.match(page, /listNotice/)
  assert.match(page, /addNotice/)
  assert.match(page, /updateNotice/)
  assert.match(page, /delNotice/)
  assert.doesNotMatch(page, /@phosphor-icons/)
  assert.doesNotMatch(page, /--color-foreground/)
})
