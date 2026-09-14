import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  validateFormFields,
  REGISTER_SEND_CODE_FIELDS,
  FORGET_SEND_CODE_FIELDS
} from './validateFormFields.js'

function createForm(results) {
  return {
    validateField(props, cb) {
      for (const prop of [].concat(props)) {
        const entry = results[prop] || {}
        cb(entry.message || '', entry.invalidFields)
      }
    }
  }
}

test('exports send-code field lists for register and forget pages', () => {
  assert.deepEqual(REGISTER_SEND_CODE_FIELDS, ['email', 'password', 'confirmPassword'])
  assert.deepEqual(FORGET_SEND_CODE_FIELDS, ['email', 'newPassword', 'confirmPassword'])
})

test('resolves valid when every field reports no message', async () => {
  const form = createForm({
    email: {},
    password: {},
    confirmPassword: {}
  })
  const result = await validateFormFields(form, REGISTER_SEND_CODE_FIELDS)
  assert.equal(result.valid, true)
  assert.deepEqual(result.fields, {})
})

test('merges a confirm-password mismatch into fields', async () => {
  const form = createForm({
    email: {},
    password: {},
    confirmPassword: {
      message: '两次输入的密码不一致',
      invalidFields: { confirmPassword: [{ message: '两次输入的密码不一致' }] }
    }
  })
  const result = await validateFormFields(form, REGISTER_SEND_CODE_FIELDS)
  assert.equal(result.valid, false)
  assert.equal(result.fields.confirmPassword[0].message, '两次输入的密码不一致')
})

test('merges errors from two fields', async () => {
  const form = createForm({
    email: {
      message: '请输入您的邮箱',
      invalidFields: { email: [{ message: '请输入您的邮箱' }] }
    },
    password: {
      message: '请输入您的密码',
      invalidFields: { password: [{ message: '请输入您的密码' }] }
    }
  })
  const result = await validateFormFields(form, ['email', 'password'])
  assert.equal(result.valid, false)
  assert.equal(result.fields.email[0].message, '请输入您的邮箱')
  assert.equal(result.fields.password[0].message, '请输入您的密码')
})

test('waits for a late field error instead of succeeding early', async () => {
  const form = {
    validateField(props, cb) {
      for (const prop of [].concat(props)) {
        if (prop === 'email') {
          cb()
          continue
        }
        setTimeout(() => {
          cb('两次输入的密码不一致', {
            confirmPassword: [{ message: '两次输入的密码不一致' }]
          })
        }, 15)
      }
    }
  }
  const result = await validateFormFields(form, ['email', 'confirmPassword'])
  assert.equal(result.valid, false)
  assert.equal(result.fields.confirmPassword[0].message, '两次输入的密码不一致')
})

test('treats empty props or missing form as valid', async () => {
  assert.deepEqual(await validateFormFields(null, ['email']), { valid: true, fields: {} })
  assert.deepEqual(await validateFormFields({}, ['email']), { valid: true, fields: {} })
  const form = createForm({ email: { message: 'x', invalidFields: { email: [{ message: 'x' }] } } })
  assert.deepEqual(await validateFormFields(form, []), { valid: true, fields: {} })
})
