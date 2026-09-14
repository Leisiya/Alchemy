import { test } from 'node:test'
import assert from 'node:assert/strict'
import { xueqiuQuoteUrl } from './xueqiuQuoteUrl.js'

test('xueqiuQuoteUrl maps Tushare tsCode to Xueqiu quote URL', () => {
  assert.equal(xueqiuQuoteUrl('000001.SZ'), 'https://xueqiu.com/S/SZ000001')
  assert.equal(xueqiuQuoteUrl('600000.SH'), 'https://xueqiu.com/S/SH600000')
  assert.equal(xueqiuQuoteUrl('688001.SH'), 'https://xueqiu.com/S/SH688001')
  assert.equal(xueqiuQuoteUrl('430047.BJ'), 'https://xueqiu.com/S/BJ430047')
  assert.equal(xueqiuQuoteUrl('000001.sz'), 'https://xueqiu.com/S/SZ000001')
  assert.equal(xueqiuQuoteUrl('  600000.SH  '), 'https://xueqiu.com/S/SH600000')
})

test('xueqiuQuoteUrl returns null for unusable codes', () => {
  assert.equal(xueqiuQuoteUrl(null), null)
  assert.equal(xueqiuQuoteUrl(undefined), null)
  assert.equal(xueqiuQuoteUrl(''), null)
  assert.equal(xueqiuQuoteUrl('—'), null)
  assert.equal(xueqiuQuoteUrl('000001'), null)
  assert.equal(xueqiuQuoteUrl('000001.HK'), null)
  assert.equal(xueqiuQuoteUrl('SZ000001'), null)
  assert.equal(xueqiuQuoteUrl('A.SH'), null)
})
