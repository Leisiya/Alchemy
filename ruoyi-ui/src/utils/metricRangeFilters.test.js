import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  METRIC_RANGE_FIELDS,
  hasInvalidRange,
  hasInvertedRange,
  omitBlankRanges,
  pickRangeQuery
} from './metricRangeFilters.js'

test('METRIC_RANGE_FIELDS uses Task 8 Java query names and toolbar labels', () => {
  assert.deepEqual(
    METRIC_RANGE_FIELDS.map(field => [field.label, field.minKey, field.maxKey]),
    [
      ['PE', 'peTtmMin', 'peTtmMax'],
      ['PB', 'pbMin', 'pbMax'],
      ['ROE', 'roeMin', 'roeMax'],
      ['股息率', 'dvTtmMin', 'dvTtmMax'],
      ['市值', 'totalMvYiMin', 'totalMvYiMax']
    ]
  )
})

test('hasInvertedRange returns the field label when min is greater than max', () => {
  assert.equal(hasInvertedRange({ peTtmMin: 20, peTtmMax: 10 }), 'PE')
  assert.equal(hasInvertedRange({ roeMin: '8', roeMax: '3' }), 'ROE')
  assert.equal(hasInvertedRange({ totalMvYiMin: 200, totalMvYiMax: 50 }), '市值')
})

test('hasInvertedRange ignores open-ended ranges with only one side filled', () => {
  assert.equal(hasInvertedRange({ peTtmMin: 20 }), null)
  assert.equal(hasInvertedRange({ peTtmMax: 10 }), null)
  assert.equal(hasInvertedRange({ peTtmMin: 20, peTtmMax: '' }), null)
  assert.equal(hasInvertedRange({ peTtmMin: '', peTtmMax: 5 }), null)
  assert.equal(hasInvertedRange({ peTtmMin: 10, peTtmMax: 10 }), null)
})

test('omitBlankRanges drops empty strings and leaves real values including zero', () => {
  const result = omitBlankRanges({
    tsCode: '000001.SZ',
    peTtmMin: '',
    peTtmMax: '10',
    pbMin: '   ',
    pbMax: 0,
    roeMin: undefined,
    name: ''
  })

  assert.equal(Object.prototype.hasOwnProperty.call(result, 'peTtmMin'), false)
  assert.equal(Object.prototype.hasOwnProperty.call(result, 'pbMin'), false)
  assert.equal(Object.prototype.hasOwnProperty.call(result, 'roeMin'), false)
  assert.equal(result.peTtmMax, 10)
  assert.equal(result.pbMax, 0)
  assert.equal(result.tsCode, '000001.SZ')
  assert.equal(result.name, '')
  assert.equal(JSON.stringify(result).includes('""'), true)
  assert.equal(JSON.stringify(result).includes('"peTtmMin"'), false)
})

test('omitBlankRanges parses percent and thousands separators into finite numbers', () => {
  const result = omitBlankRanges({
    roeMin: '8.50%',
    totalMvYiMin: '1,234',
    totalMvYiMax: '1,234.56',
    dvTtmMax: '8.50 %'
  })

  assert.equal(result.roeMin, 8.5)
  assert.equal(result.totalMvYiMin, 1234)
  assert.equal(result.totalMvYiMax, 1234.56)
  assert.equal(result.dvTtmMax, 8.5)
  assert.equal(Number.isFinite(result.roeMin), true)
  assert.equal(Number.isFinite(result.totalMvYiMin), true)
})

test('invalid range text is reported and omitted from the request payload', () => {
  assert.equal(hasInvalidRange({ roeMin: 'abc' }), 'ROE')
  assert.equal(hasInvalidRange({ totalMvYiMax: '12x' }), '市值')
  assert.equal(hasInvalidRange({ roeMin: '8.50%' }), null)
  assert.equal(hasInvalidRange({ totalMvYiMin: '1,234' }), null)
  assert.equal(hasInvalidRange({ peTtmMin: '' }), null)

  const result = omitBlankRanges({
    tsCode: '000001.SZ',
    roeMin: 'abc',
    peTtmMax: '10'
  })
  assert.equal(Object.prototype.hasOwnProperty.call(result, 'roeMin'), false)
  assert.equal(result.tsCode, '000001.SZ')
})

test('hasInvertedRange still works after parsing percent and thousands separators', () => {
  assert.equal(hasInvertedRange({ roeMin: '8.50%', roeMax: '3%' }), 'ROE')
  assert.equal(hasInvertedRange({ totalMvYiMin: '2,000', totalMvYiMax: '1,000' }), '市值')
  assert.equal(hasInvertedRange({ dvTtmMin: '3%', dvTtmMax: '8.50%' }), null)
  assert.equal(hasInvertedRange({ roeMin: '8.50%', roeMax: '' }), null)
})

test('pickRangeQuery parses route query strings so numeric comparison works', () => {
  const picked = pickRangeQuery({
    tsCode: '600519.SH',
    peTtmMin: '20',
    peTtmMax: '10',
    roeMin: '8',
    dvTtmMax: '',
    pageNum: '2'
  })

  assert.equal(Object.prototype.hasOwnProperty.call(picked, 'tsCode'), false)
  assert.equal(Object.prototype.hasOwnProperty.call(picked, 'pageNum'), false)
  assert.equal(Object.prototype.hasOwnProperty.call(picked, 'dvTtmMax'), false)
  assert.equal(hasInvertedRange(picked), 'PE')
  assert.equal(Number(picked.roeMin), 8)
})
