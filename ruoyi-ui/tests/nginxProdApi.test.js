'use strict'

const fs = require('fs')
const path = require('path')
const { test } = require('node:test')
const assert = require('node:assert/strict')

const conf = fs.readFileSync(
  path.join(__dirname, '../../deploy/nginx-locations.conf'),
  'utf8'
)

test('prod-api prefix uses ^~ so Druid js/css are not stolen by static regex', () => {
  assert.match(conf, /location \^~ \/prod-api\//)
  assert.match(conf, /location ~\* \\\.\(\?:js\|css/)
})
