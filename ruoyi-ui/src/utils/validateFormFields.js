export const REGISTER_SEND_CODE_FIELDS = ['email', 'password', 'confirmPassword']

export const FORGET_SEND_CODE_FIELDS = ['email', 'newPassword', 'confirmPassword']

export function validateFormFields(form, props) {
  const list = [].concat(props || []).filter(Boolean)
  return new Promise((resolve) => {
    if (!form || typeof form.validateField !== 'function' || list.length === 0) {
      resolve({ valid: true, fields: {} })
      return
    }
    const merged = {}
    let pending = list.length
    let valid = true
    form.validateField(list, (message, invalidFields) => {
      pending--
      if (message) {
        valid = false
        if (invalidFields && typeof invalidFields === 'object') {
          Object.assign(merged, invalidFields)
        }
      }
      if (pending === 0) {
        resolve({ valid, fields: merged })
      }
    })
  })
}
