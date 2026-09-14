const TS_CODE = /^(\d{6})\.(SH|SZ|BJ)$/i

export function xueqiuQuoteUrl(tsCode) {
  if (tsCode == null) {
    return null
  }
  const match = String(tsCode).trim().match(TS_CODE)
  if (!match) {
    return null
  }
  return 'https://xueqiu.com/S/' + match[2].toUpperCase() + match[1]
}
