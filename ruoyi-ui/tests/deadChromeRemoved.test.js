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

const gone = [
  'src/views/index_v1.vue',
  'src/views/dashboard',
  'src/components/HeaderSearch',
  'src/components/Screenfull',
  'src/components/SizeSelect',
  'src/components/Breadcrumb',
  'src/components/PanThumb',
  'src/components/TreePanel',
  'src/utils/permission.js',
  'src/directive/dialog',
  'src/assets/images/login-background.jpg',
  'src/assets/images/pay.png',
  'src/assets/images/dark.svg',
  'src/assets/images/light.svg',
  'src/assets/icons/svg/message.svg',
  'src/assets/icons/svg/money.svg'
]

for (const rel of gone) {
  test(`${rel} is gone`, () => {
    assert.equal(fs.existsSync(path.join(uiRoot, rel)), false)
  })
}

test('package.json dropped unused chrome deps', () => {
  const pkg = read('package.json')
  assert.doesNotMatch(pkg, /"fuse\.js"/)
  assert.doesNotMatch(pkg, /"screenfull"/)
  assert.doesNotMatch(pkg, /"vue-count-to"/)
})

test('directive registry does not install dialog drag', () => {
  const src = read('src/directive/index.js')
  assert.doesNotMatch(src, /dialogDrag/)
  assert.doesNotMatch(src, /dialog\/drag/)
})

test('swagger fake-user TestController is gone', () => {
  assert.equal(
    fs.existsSync(path.join(
      repoRoot,
      'ruoyi-admin/src/main/java/com/ruoyi/web/controller/tool/TestController.java'
    )),
    false
  )
})

test('legacy start-ruoyi-admin script is gone', () => {
  assert.equal(fs.existsSync(path.join(repoRoot, 'scripts/start-ruoyi-admin.sh')), false)
})

test('unused origin-tls-proxy nginx draft is gone', () => {
  assert.equal(fs.existsSync(path.join(repoRoot, 'deploy/origin-tls-proxy.conf')), false)
})

test('root design-system stub is gone', () => {
  assert.equal(fs.existsSync(path.join(repoRoot, 'design-system')), false)
})
