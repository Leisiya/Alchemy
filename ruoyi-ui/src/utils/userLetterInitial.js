export function userLetterInitial(nickName, userName) {
  const source = String(nickName || '').trim() || String(userName || '').trim()
  return source ? source.charAt(0).toUpperCase() : '?'
}
