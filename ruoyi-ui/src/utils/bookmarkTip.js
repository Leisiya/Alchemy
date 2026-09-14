'use strict'

const LOCAL_KEY = 'alchemy-bookmark-tip-dismissed'
const SESSION_KEY = 'alchemy-bookmark-tip-dismissed-session'

const APPLE_PATTERN = /Mac|iPhone|iPad|iPod/i

function shortcutHint(userAgent, platform) {
  if (APPLE_PATTERN.test(platform) || APPLE_PATTERN.test(userAgent)) {
    return '⌘ + D'
  }
  return 'Ctrl + D'
}

function shouldShowBookmarkTip({ dismissedForever, dismissedSession, device }) {
  if (dismissedForever || dismissedSession) {
    return false
  }
  if (device === 'mobile') {
    return false
  }
  return true
}

function readDismissed(localStore, sessionStore) {
  return {
    dismissedForever: localStore.get(LOCAL_KEY) === '1',
    dismissedSession: sessionStore.get(SESSION_KEY) === '1'
  }
}

function persistDismiss({ dontShowAgain, localStore, sessionStore }) {
  if (dontShowAgain) {
    localStore.set(LOCAL_KEY, '1')
  } else {
    sessionStore.set(SESSION_KEY, '1')
  }
}

module.exports = {
  LOCAL_KEY,
  SESSION_KEY,
  shortcutHint,
  shouldShowBookmarkTip,
  readDismissed,
  persistDismiss
}
