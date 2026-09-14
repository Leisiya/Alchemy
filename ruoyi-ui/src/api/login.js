import request from '@/utils/request'

// 登录方法
export function login(username, password, code, uuid) {
  const data = {
    username,
    password,
    code,
    uuid
  }
  return request({
    url: '/login',
    headers: {
      isToken: false,
      repeatSubmit: false
    },
    method: 'post',
    data: data
  })
}

export function guestLogin() {
  return request({
    url: '/login/guest',
    headers: {
      isToken: false,
      repeatSubmit: false
    },
    method: 'post'
  })
}

// 注册方法
export function register(data) {
  return request({
    url: '/register',
    headers: {
      isToken: false
    },
    method: 'post',
    data: data
  })
}

// 发送注册邮箱验证码
export function sendEmailCode(email) {
  return request({
    url: '/register/emailCode',
    headers: {
      isToken: false
    },
    method: 'post',
    params: { email }
  })
}

// 发送找回密码邮箱验证码
export function sendResetPwdEmailCode(email) {
  return request({
    url: '/resetPwd/emailCode',
    headers: {
      isToken: false
    },
    method: 'post',
    params: { email }
  })
}

// 通过邮箱验证码重置密码
export function resetPwdByEmail(data) {
  return request({
    url: '/resetPwd/byEmail',
    headers: {
      isToken: false
    },
    method: 'post',
    data: data
  })
}

// 获取用户详细信息
export function getInfo() {
  return request({
    url: '/getInfo',
    method: 'get'
  })
}

// 退出方法
export function logout() {
  return request({
    url: '/logout',
    method: 'post'
  })
}

// 获取验证码
export function getCodeImg() {
  return request({
    url: '/captchaImage',
    headers: {
      isToken: false
    },
    method: 'get',
    timeout: 20000
  })
}