import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { applyFormErrors } from './authErrorSummary.js'

const viewsDir = path.join(path.dirname(fileURLToPath(import.meta.url)), '../views')

function withGetElementById(lookup, run) {
  const previous = globalThis.document
  globalThis.document = {
    getElementById(id) {
      return lookup(id)
    }
  }
  try {
    return run()
  } finally {
    globalThis.document = previous
  }
}

test('returns true and does not focus when the form is valid', () => {
  const focused = []
  const vm = { $nextTick(fn) { fn() } }
  withGetElementById(() => ({ focus() { focused.push('hit') } }), () => {
    assert.equal(applyFormErrors(vm, true, { email: [{ message: 'x' }] }), true)
  })
  assert.deepEqual(focused, [])
})

test('focuses the first invalid field after failed submit', () => {
  const focused = []
  const email = { focus() { focused.push('email') } }
  const vm = {
    $refs: { errorSummary: { focus() { focused.push('summary') } } },
    $nextTick(fn) { fn() }
  }
  const ok = withGetElementById(
    (id) => (id === 'email' ? email : null),
    () => applyFormErrors(vm, false, {
      email: [{ message: '请输入您的邮箱' }],
      password: [{ message: '请输入您的密码' }]
    })
  )
  assert.equal(ok, false)
  assert.deepEqual(focused, ['email'])
})

test('login register and forget pages have no top error summary', () => {
  for (const file of ['login.vue', 'register.vue', 'forgetPassword.vue']) {
    const source = fs.readFileSync(path.join(viewsDir, file), 'utf8')
    assert.equal(source.includes('auth-error-summary'), false, file)
    assert.equal(source.includes('errorSummary'), false, file)
  }
})
