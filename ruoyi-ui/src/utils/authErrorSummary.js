export function applyFormErrors(vm, valid, invalidFields) {
  if (valid) {
    return true
  }
  const firstProp = Object.keys(invalidFields || {})[0]
  vm.$nextTick(() => {
    const el = firstProp && typeof document !== 'undefined' && document.getElementById(firstProp)
    if (el && typeof el.focus === 'function') {
      el.focus()
    }
  })
  return false
}
