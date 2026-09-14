import { test } from 'node:test'
import assert from 'node:assert/strict'
import { userLetterInitial } from './userLetterInitial.js'

test('uses first letter of userName when nickName is empty', () => {
  assert.equal(userLetterInitial('', 'andrewcode'), 'A')
})

test('prefers trimmed nickName over userName', () => {
  assert.equal(userLetterInitial('  bob', 'andrewcode'), 'B')
})

test('uppercases a lowercase first character', () => {
  assert.equal(userLetterInitial('andrewcode', ''), 'A')
})

test('keeps a CJK first character', () => {
  assert.equal(userLetterInitial('张三', 'andrewcode'), '张')
})

test('returns question mark when both are blank', () => {
  assert.equal(userLetterInitial('  ', ''), '?')
  assert.equal(userLetterInitial(undefined, null), '?')
})
