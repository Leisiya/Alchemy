'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const uiRoot = path.join(__dirname, '..')
const repoRoot = path.join(__dirname, '../..')

function readRepo(rel) {
  return fs.readFileSync(path.join(repoRoot, rel), 'utf8')
}

test('ruoyi-generator module is gone', () => {
  assert.equal(fs.existsSync(path.join(repoRoot, 'ruoyi-generator')), false)
})

test('root pom does not declare ruoyi-generator', () => {
  const pom = readRepo('pom.xml')
  assert.doesNotMatch(pom, /ruoyi-generator/)
  assert.doesNotMatch(pom, /velocity-engine-core/)
})

test('admin pom does not depend on ruoyi-generator', () => {
  assert.doesNotMatch(readRepo('ruoyi-admin/pom.xml'), /ruoyi-generator/)
})

test('frontend gen pages and api are gone', () => {
  assert.equal(fs.existsSync(path.join(uiRoot, 'src/views/tool/gen')), false)
  assert.equal(fs.existsSync(path.join(uiRoot, 'src/api/tool/gen.js')), false)
})

test('router has no gen-edit dynamic route', () => {
  assert.doesNotMatch(readRepo('ruoyi-ui/src/router/index.js'), /tool\/gen/)
})

test('clipboard directive is gone', () => {
  assert.equal(fs.existsSync(path.join(uiRoot, 'src/directive/module/clipboard.js')), false)
  const dir = readRepo('ruoyi-ui/src/directive/index.js')
  assert.doesNotMatch(dir, /clipboard/)
})

test('seed sql has no code-gen menu or tables', () => {
  const sql = readRepo('sql/ry_20260417.sql')
  assert.doesNotMatch(sql, /tool:gen/)
  assert.doesNotMatch(sql, /gen_table/)
})

const removedSystemToolMenuPattern =
  /insert into sys_menu values\('(3|5|115|117|118)'/i

test('seed sql has no system-tool or nested stock-list menus', () => {
  const sql = readRepo('sql/ry_20260417.sql')
  assert.doesNotMatch(sql, /tool:build/)
  assert.doesNotMatch(sql, /tool:swagger/)
  assert.doesNotMatch(sql, removedSystemToolMenuPattern)
})

test('seed sql keeps screener F-button permissions with root parent', () => {
  const sql = readRepo('sql/ry_20260417.sql')
  assert.match(sql, /stock:screener:query/)
  assert.match(sql, /stock:screener:export/)
  assert.match(sql, /stock:screener:list/)
  assert.match(sql, /insert into sys_menu values\('1061',[^)]*'0',/)
  assert.match(sql, /insert into sys_menu values\('1062',[^)]*'0',/)
  assert.match(sql, /insert into sys_menu values\('1063',[^)]*'0',/)
  assert.doesNotMatch(sql, /insert into sys_menu values\('1061',[^)]*'118',/)
  assert.doesNotMatch(sql, /insert into sys_menu values\('1062',[^)]*'118',/)
  assert.doesNotMatch(sql, /insert into sys_menu values\('1063',[^)]*'118',/)
})

test('patch_drop_system_tools.sql drops menus and reparents F-buttons', () => {
  const patch = readRepo('sql/patch_drop_system_tools.sql')
  assert.match(
    patch,
    /delete from sys_role_menu where menu_id in \(3, 115, 117, 5, 118\)/i
  )
  assert.match(
    patch,
    /update sys_menu set parent_id = 0 where menu_id in \(1061, 1062, 1063\)/i
  )
  assert.match(
    patch,
    /delete from sys_menu where menu_id in \(3, 115, 117, 5, 118\)/i
  )
  const roleMenuIdx = patch.search(/delete from sys_role_menu/i)
  const reparentIdx = patch.search(/update sys_menu set parent_id = 0/i)
  const menuDeleteIdx = patch.search(/delete from sys_menu where menu_id in \(3/i)
  assert.ok(roleMenuIdx < reparentIdx, 'role_menu delete must precede reparent')
  assert.ok(reparentIdx < menuDeleteIdx, 'reparent must precede menu delete')
})

function readUi(rel) {
  return fs.readFileSync(path.join(uiRoot, rel), 'utf8')
}

function readUiJson(rel) {
  return JSON.parse(readUi(rel))
}

test('form builder and swagger tool pages are gone', () => {
  assert.equal(fs.existsSync(path.join(uiRoot, 'src/views/tool/build')), false)
  assert.equal(fs.existsSync(path.join(uiRoot, 'src/views/tool/swagger')), false)
})

test('form builder generator utils are gone', () => {
  assert.equal(fs.existsSync(path.join(uiRoot, 'src/utils/generator')), false)
})

test('package.json drops form-builder-only dependencies', () => {
  const pkg = readUiJson('package.json')
  const deps = { ...pkg.dependencies, ...pkg.devDependencies }
  assert.equal('vuedraggable' in deps, false)
  assert.equal('js-beautify' in deps, false)
  assert.equal('clipboard' in deps, false)
})

test('vue.config.js has no springdoc proxy', () => {
  const config = readUi('vue.config.js')
  assert.doesNotMatch(config, /\/v3\/api-docs/)
  assert.doesNotMatch(config, /springdoc/i)
})

test('utils index has no beautifierConf export', () => {
  assert.doesNotMatch(readUi('src/utils/index.js'), /beautifierConf/)
})

test('router keeps screener product routes', () => {
  const router = readRepo('ruoyi-ui/src/router/index.js')
  assert.match(router, /path:\s*'index'/)
  assert.match(router, /title:\s*'股票列表'/)
  assert.match(router, /path:\s*'\/stock\/undervalued'/)
  assert.match(router, /path:\s*'\/stock\/breakout'/)
  assert.match(router, /path:\s*'\/stock\/watchlist'/)
})

test('SwaggerConfig.java is gone', () => {
  assert.equal(
    fs.existsSync(
      path.join(
        repoRoot,
        'ruoyi-admin/src/main/java/com/ruoyi/web/core/config/SwaggerConfig.java'
      )
    ),
    false
  )
})

test('root pom has no springdoc', () => {
  const pom = readRepo('pom.xml')
  assert.doesNotMatch(pom, /springdoc/i)
})

test('admin pom has no springdoc-openapi-starter-webmvc-ui', () => {
  assert.doesNotMatch(readRepo('ruoyi-admin/pom.xml'), /springdoc-openapi-starter-webmvc-ui/)
})

test('application.yml has no springdoc key', () => {
  assert.doesNotMatch(readRepo('ruoyi-admin/src/main/resources/application.yml'), /^springdoc:/m)
})

test('ResourcesConfig has no swagger resource handler', () => {
  const config = readRepo(
    'ruoyi-framework/src/main/java/com/ruoyi/framework/config/ResourcesConfig.java'
  )
  assert.doesNotMatch(config, /\/swagger-ui\/\*\*/)
  assert.doesNotMatch(config, /springfox-swagger-ui/)
})

test('SecurityConfig keeps druid permitAll but not swagger paths', () => {
  const config = readRepo(
    'ruoyi-framework/src/main/java/com/ruoyi/framework/config/SecurityConfig.java'
  )
  assert.match(config, /\/druid\/\*\*.*permitAll\(\)/)
  assert.doesNotMatch(config, /\/swagger-ui\.html/)
  assert.doesNotMatch(config, /\/v3\/api-docs\/\*\*/)
  assert.doesNotMatch(config, /\/swagger-ui\/\*\*/)
})

test('alchemy.mdc does not point debug workflow at swagger or build', () => {
  const rule = readRepo('.cursor/rules/alchemy.mdc')
  assert.doesNotMatch(rule, /\/tool\/swagger/)
  assert.doesNotMatch(rule, /\/tool\/build/)
  assert.match(rule, /\/tool\/gen/)
  assert.match(rule, /已移除|模块已移除/)
})

test('agent docs do not point debug workflow at swagger or build', () => {
  const files = [
    'docs/agent/alchemy/conventions.md',
    'docs/agent/README.md',
    'docs/agent/ruoyi-vue/overview.md',
  ]
  for (const rel of files) {
    const content = readRepo(rel)
    assert.doesNotMatch(content, /\/tool\/swagger/, `${rel} must not mention /tool/swagger`)
    assert.doesNotMatch(content, /\/tool\/build/, `${rel} must not mention /tool/build`)
  }
})

test('backend.md does not document swagger or springdoc', () => {
  const backend = readRepo('docs/agent/ruoyi-vue/backend.md')
  assert.doesNotMatch(backend, /\/tool\/swagger/)
  assert.doesNotMatch(backend, /springdoc/i)
})

test('faq.md does not document swagger paths or springdoc.swagger-ui', () => {
  const faq = readRepo('docs/agent/ruoyi-vue/faq.md')
  assert.doesNotMatch(faq, /\/tool\/swagger/)
  assert.doesNotMatch(faq, /springdoc\.swagger-ui/)
})

test('plugins.md does not list SpringDoc as configured', () => {
  assert.doesNotMatch(readRepo('docs/agent/ruoyi-vue/plugins.md'), /SpringDoc/)
})

test('components.md does not document form builder', () => {
  assert.doesNotMatch(readRepo('docs/agent/ruoyi-vue/components.md'), /表单构建/)
})

test('deploy.md nginx example does not proxy api-docs', () => {
  assert.doesNotMatch(readRepo('docs/agent/ruoyi-vue/deploy.md'), /api-docs/)
})
