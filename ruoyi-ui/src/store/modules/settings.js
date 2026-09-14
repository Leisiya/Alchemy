import defaultSettings from '@/settings'
import { useDynamicTitle } from '@/utils/dynamicTitle'
import productChrome from '@/utils/productChrome'

const { sideTheme, showSettings, navType, tagsViewPersist, tagsIcon, tagsViewStyle, fixedHeader, sidebarLogo, dynamicTitle, footerVisible, footerContent } = defaultSettings

if (typeof localStorage !== 'undefined') {
  productChrome.clearStoredLayoutSetting(localStorage)
}

const state = {
  title: '',
  theme: productChrome.PRODUCT_THEME,
  sideTheme: sideTheme,
  showSettings: showSettings,
  navType: navType,
  tagsView: false,
  tagsViewPersist: tagsViewPersist,
  tagsIcon: tagsIcon,
  tagsViewStyle: tagsViewStyle,
  fixedHeader: fixedHeader,
  sidebarLogo: sidebarLogo,
  dynamicTitle: dynamicTitle,
  footerVisible: footerVisible,
  footerContent: footerContent
}
const mutations = {
  CHANGE_SETTING: (state, { key, value }) => {
    if (key === 'tagsView') {
      state.tagsView = false
      return
    }
    if (state.hasOwnProperty(key)) {
      state[key] = value
    }
  },
  SET_TITLE: (state, title) => {
    state.title = title
  }
}

const actions = {
  changeSetting({ commit }, data) {
    commit('CHANGE_SETTING', data)
  },
  setTitle({ commit }, title) {
    commit('SET_TITLE', title)
    useDynamicTitle()
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
