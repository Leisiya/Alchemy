import {
  listInbox,
  getNoticeUnreadCount,
  markNoticeRead,
  markNoticeReadAll
} from '@/api/system/notice'
import noticeInbox from '@/utils/noticeInbox'

const {
  STORAGE_KEY,
  applyGuestReadOverlay,
  guestUnreadCount,
  parseGuestReadIds,
  appendGuestReadId,
  appendAllGuestReadIds
} = noticeInbox

function ajaxData(res) {
  if (res && res.data !== undefined) {
    return res.data
  }
  return res
}

function readGuestIds() {
  return parseGuestReadIds(localStorage.getItem(STORAGE_KEY))
}

function overlayList(list) {
  return applyGuestReadOverlay(list || [], readGuestIds())
}

function countUnread(list) {
  return (list || []).filter(item => !item.isRead).length
}

function sameNotice(item, noticeId) {
  return Number(item.noticeId) === Number(noticeId)
}

const state = {
  unreadCount: 0,
  drawerVisible: false,
  list: [],
  activeId: null,
  loading: false,
  error: null
}

const mutations = {
  SET_UNREAD_COUNT: (state, count) => {
    state.unreadCount = count || 0
  },
  SET_DRAWER_VISIBLE: (state, visible) => {
    state.drawerVisible = visible
  },
  SET_LIST: (state, list) => {
    state.list = list || []
  },
  SET_ACTIVE_ID: (state, id) => {
    state.activeId = id
  },
  SET_LOADING: (state, loading) => {
    state.loading = loading
  },
  SET_ERROR: (state, error) => {
    state.error = error
  }
}

const actions = {
  fetchUnread({ commit, rootGetters }) {
    if (rootGetters.isGuest) {
      return listInbox().then(res => {
        const list = overlayList(ajaxData(res) || [])
        commit('SET_UNREAD_COUNT', guestUnreadCount(list, readGuestIds()))
      }).catch(() => {})
    }
    return getNoticeUnreadCount().then(res => {
      commit('SET_UNREAD_COUNT', Number(ajaxData(res)) || 0)
    }).catch(() => {})
  },
  openDrawer({ commit, rootGetters }) {
    commit('SET_DRAWER_VISIBLE', true)
    commit('SET_ACTIVE_ID', null)
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    return listInbox().then(res => {
      let list = ajaxData(res) || []
      if (rootGetters.isGuest) {
        list = overlayList(list)
      }
      commit('SET_LIST', list)
      commit('SET_UNREAD_COUNT', countUnread(list))
      commit('SET_LOADING', false)
    }).catch(() => {
      commit('SET_ERROR', true)
      commit('SET_LOADING', false)
    })
  },
  closeDrawer({ commit }) {
    commit('SET_DRAWER_VISIBLE', false)
    commit('SET_ACTIVE_ID', null)
  },
  openItem({ commit, state, rootGetters }, noticeId) {
    commit('SET_ACTIVE_ID', noticeId)
    const current = state.list.find(item => sameNotice(item, noticeId))
    if (current && current.isRead) {
      return Promise.resolve()
    }
    if (rootGetters.isGuest) {
      const nextRaw = appendGuestReadId(localStorage.getItem(STORAGE_KEY), noticeId)
      localStorage.setItem(STORAGE_KEY, nextRaw)
      const list = applyGuestReadOverlay(state.list, parseGuestReadIds(nextRaw))
      commit('SET_LIST', list)
      commit('SET_UNREAD_COUNT', guestUnreadCount(list, parseGuestReadIds(nextRaw)))
      return Promise.resolve()
    }
    return markNoticeRead(noticeId).then(() => {
      const list = state.list.map(item => {
        return sameNotice(item, noticeId) ? { ...item, isRead: true } : item
      })
      commit('SET_LIST', list)
      commit('SET_UNREAD_COUNT', countUnread(list))
    }).catch(() => {})
  },
  markAll({ commit, state, rootGetters }) {
    if (rootGetters.isGuest) {
      const ids = state.list.map(item => item.noticeId)
      const nextRaw = appendAllGuestReadIds(localStorage.getItem(STORAGE_KEY), ids)
      localStorage.setItem(STORAGE_KEY, nextRaw)
      const list = applyGuestReadOverlay(state.list, parseGuestReadIds(nextRaw))
      commit('SET_LIST', list)
      commit('SET_UNREAD_COUNT', 0)
      return Promise.resolve()
    }
    return markNoticeReadAll().then(() => {
      const list = state.list.map(item => ({ ...item, isRead: true }))
      commit('SET_LIST', list)
      commit('SET_UNREAD_COUNT', 0)
    }).catch(() => {})
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
