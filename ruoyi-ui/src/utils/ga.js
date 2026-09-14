export function getGaMeasurementId() {
  return String(process.env.VUE_APP_GA_MEASUREMENT_ID || '').trim()
}

export function shouldTrackGa(measurementId = getGaMeasurementId()) {
  return Boolean(measurementId && String(measurementId).trim())
}

export function buildPageviewPayload(path, title) {
  return {
    page_path: path || '/',
    page_title: title || ''
  }
}

export function initGa() {
  const measurementId = getGaMeasurementId()
  if (!shouldTrackGa(measurementId) || typeof window === 'undefined' || typeof document === 'undefined') {
    return false
  }
  if (typeof window.gtag === 'function') {
    return true
  }
  window.dataLayer = window.dataLayer || []
  window.gtag = function gtag() {
    window.dataLayer.push(arguments)
  }
  const script = document.createElement('script')
  script.async = true
  script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId)
  document.head.appendChild(script)
  window.gtag('js', new Date())
  window.gtag('config', measurementId, { send_page_view: false })
  return true
}

export function trackPageview(path, title, options = {}) {
  const measurementId = options.measurementId !== undefined ? options.measurementId : getGaMeasurementId()
  const send = options.gtag || (typeof window !== 'undefined' ? window.gtag : undefined)
  if (!shouldTrackGa(measurementId) || typeof send !== 'function') {
    return false
  }
  send('event', 'page_view', buildPageviewPayload(path, title))
  return true
}
