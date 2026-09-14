import router from '@/router'
import cache from '@/plugins/cache'
import { MessageBox } from 'element-ui'
import { login, guestLogin, logout, getInfo } from '@/api/login'
import { getToken, setToken, removeToken } from '@/utils/auth'
import { isHttp } from "@/utils/validate"

const user = {
  state: {
    token: getToken(),
    id: '',
    name: '',
    nickName: '',
    avatar: '',
    roles: [],
    permissions: [],
    isGuest: false
  },

  mutations: {
    SET_TOKEN: (state, token) => {
      state.token = token
    },
    SET_ID: (state, id) => {
      state.id = id
    },
    SET_NAME: (state, name) => {
      state.name = name
    },
    SET_NICK_NAME: (state, nickName) => {
      state.nickName = nickName
    },
    SET_AVATAR: (state, avatar) => {
      state.avatar = avatar
    },
    SET_ROLES: (state, roles) => {
      state.roles = roles
    },
    SET_PERMISSIONS: (state, permissions) => {
      state.permissions = permissions
    },
    SET_IS_GUEST: (state, isGuest) => {
      state.isGuest = isGuest
    }
  },

  actions: {
    ApplyToken({ commit }, token) {
      return new Promise(resolve => {
        setToken(token)
        commit('SET_TOKEN', token)
        resolve()
      })
    },
    // 登录
    Login({ dispatch }, userInfo) {
      const username = userInfo.username.trim()
      const password = userInfo.password
      const code = userInfo.code
      const uuid = userInfo.uuid
      return new Promise((resolve, reject) => {
        login(username, password, code, uuid).then(res => {
          dispatch('ApplyToken', res.token).then(() => resolve())
        }).catch(error => {
          reject(error)
        })
      })
    },
    GuestLogin({ dispatch }) {
      return new Promise((resolve, reject) => {
        guestLogin().then(res => {
          dispatch('ApplyToken', res.token).then(() => resolve())
        }).catch(error => {
          reject(error)
        })
      })
    },

    // 获取用户信息
    GetInfo({ commit, state }) {
      return new Promise((resolve, reject) => {
        getInfo().then(res => {
          const user = res.user
          let avatar = user.avatar || ''
          if (avatar && !isHttp(avatar)) {
            avatar = process.env.VUE_APP_BASE_API + avatar
          }
          if (res.roles && res.roles.length > 0) { // 验证返回的roles是否是一个非空数组
            commit('SET_ROLES', res.roles)
            commit('SET_PERMISSIONS', res.permissions)
          } else {
            commit('SET_ROLES', ['ROLE_DEFAULT'])
          }
          commit('SET_ID', user.userId)
          commit('SET_NAME', user.userName)
          commit('SET_NICK_NAME', user.nickName)
          commit('SET_AVATAR', avatar)
          commit('SET_IS_GUEST', res.isGuest === true)
          cache.session.set('pwrChrtype', res.pwdChrtype)
          /* 初始密码提示 */
          if (!state.isGuest && res.isDefaultModifyPwd) {
            MessageBox.confirm('您的密码还是初始密码，请修改密码！',  '安全提示', {  confirmButtonText: '确定',  cancelButtonText: '取消',  type: 'warning' }).then(() => {
              router.push({ name: 'Profile', params: { activeTab: 'resetPwd' } })
            }).catch(() => {})
          }
          /* 过期密码提示 */
          if (!state.isGuest && !res.isDefaultModifyPwd && res.isPasswordExpired) {
            MessageBox.confirm('您的密码已过期，请尽快修改密码！',  '安全提示', {  confirmButtonText: '确定',  cancelButtonText: '取消',  type: 'warning' }).then(() => {
              router.push({ name: 'Profile', params: { activeTab: 'resetPwd' } })
            }).catch(() => {})
          }
          resolve(res)
        }).catch(error => {
          reject(error)
        })
      })
    },

    // 退出系统
    LogOut({ commit, state }) {
      return new Promise((resolve, reject) => {
        logout(state.token).then(() => {
          commit('SET_TOKEN', '')
          commit('SET_ROLES', [])
          commit('SET_PERMISSIONS', [])
          commit('SET_IS_GUEST', false)
          removeToken()
          resolve()
        }).catch(error => {
          reject(error)
        })
      })
    },

    // 前端 登出
    FedLogOut({ commit }) {
      return new Promise(resolve => {
        commit('SET_TOKEN', '')
        commit('SET_IS_GUEST', false)
        removeToken()
        resolve()
      })
    }
  }
}

export default user
