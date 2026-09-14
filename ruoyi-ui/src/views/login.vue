<template>
  <div class="auth-page">
    <el-form
      ref="loginForm"
      :model="loginForm"
      :rules="loginRules"
      class="auth-form"
      hide-required-asterisk
      @submit.native.prevent="handleLogin"
    >
      <h1 class="auth-title">{{ title }}</h1>
      <p class="auth-subtitle">A股价值投资好助手</p>
      <auth-mode-switch current="login" :register-enabled="registerEnabled" />
      <el-form-item prop="username">
        <el-input
          id="username"
          v-model="loginForm.username"
          type="text"
          autocomplete="username"
          aria-label="请输入邮箱"
          placeholder="请输入邮箱"
        >
          <svg-icon slot="prefix" icon-class="user" class="el-input__icon input-icon" aria-hidden="true" />
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          id="password"
          v-model="loginForm.password"
          type="password"
          autocomplete="current-password"
          aria-label="请输入密码"
          placeholder="请输入密码"
        >
          <svg-icon slot="prefix" icon-class="password" class="el-input__icon input-icon" aria-hidden="true" />
        </el-input>
      </el-form-item>
      <el-form-item prop="code" v-if="captchaEnabled">
        <el-input
          id="code"
          v-model="loginForm.code"
          autocomplete="off"
          aria-label="请输入图形验证码"
          placeholder="请输入图形验证码"
          style="width: 63%"
        >
          <svg-icon slot="prefix" icon-class="validCode" class="el-input__icon input-icon" aria-hidden="true" />
        </el-input>
        <div class="auth-code">
          <button type="button" class="auth-code-btn" aria-label="刷新验证码" @click="getCode">
            <img :src="codeUrl" alt="图形验证码，点击刷新" />
          </button>
        </div>
      </el-form-item>
      <div class="auth-row">
        <el-checkbox v-model="loginForm.rememberMe">记住密码</el-checkbox>
        <router-link class="auth-link" :to="{ path: '/forgetPassword', query: $route.query }">忘记密码?</router-link>
      </div>
      <el-form-item style="width:100%;">
        <el-button
          :loading="loading"
          size="medium"
          type="primary"
          native-type="submit"
          style="width:100%;"
        >
          <span v-if="!loading">登录</span>
          <span v-else>登录中...</span>
        </el-button>
      </el-form-item>
      <el-form-item v-if="guestEnabled" style="width:100%;">
        <button
          type="button"
          class="auth-guest-btn"
          :disabled="loading || guestLoading"
          aria-label="访客体验"
          @click="handleGuestLogin"
        >
          <span v-if="!guestLoading">访客体验</span>
          <span v-else>进入中...</span>
        </button>
      </el-form-item>
    </el-form>
    <div class="auth-footer">
      <span>{{ footerContent }}</span>
    </div>
  </div>
</template>

<script>
import { getCodeImg } from "@/api/login"
import Cookies from "js-cookie"
import { encrypt, decrypt } from '@/utils/jsencrypt'
import defaultSettings from '@/settings'
import { applyFormErrors } from '@/utils/authErrorSummary'
import { resolvePostAuthPath } from '@/utils/authRedirect'
import AuthModeSwitch from '@/components/AuthModeSwitch'

export default {
  name: "Login",
  components: { AuthModeSwitch },
  data() {
    return {
      title: process.env.VUE_APP_TITLE,
      footerContent: defaultSettings.footerContent,
      codeUrl: "",
      loginForm: {
        username: "",
        password: "",
        rememberMe: false,
        code: "",
        uuid: ""
      },
      loginRules: {
        username: [
          { required: true, trigger: "blur", message: "请输入您的邮箱" }
        ],
        password: [
          { required: true, trigger: "blur", message: "请输入您的密码" }
        ],
        code: [{ required: true, trigger: "change", message: "请输入验证码" }]
      },
      loading: false,
      guestLoading: false,
      guestEnabled: true,
      captchaEnabled: false,
      registerEnabled: true
    }
  },
  created() {
    this.getCode()
    this.getCookie()
  },
  methods: {
    getCode() {
      getCodeImg().then(res => {
        this.captchaEnabled = res.captchaEnabled === true
        this.registerEnabled = res.registerEnabled !== false
        this.guestEnabled = res.guestEnabled !== false
        if (this.captchaEnabled) {
          this.codeUrl = "data:image/gif;base64," + res.img
          this.loginForm.uuid = res.uuid
        }
      })
    },
    getCookie() {
      const username = Cookies.get("username")
      const password = Cookies.get("password")
      const rememberMe = Cookies.get('rememberMe')
      this.loginForm.username = username === undefined ? "" : username
      this.loginForm.password = password === undefined ? "" : decrypt(password)
      this.loginForm.rememberMe = rememberMe === undefined ? false : Boolean(rememberMe)
    },
    handleLogin() {
      this.$refs.loginForm.validate((valid, fields) => {
        if (!applyFormErrors(this, valid, fields)) {
          return
        }
        this.loading = true
        if (this.loginForm.rememberMe) {
          Cookies.set("username", this.loginForm.username, { expires: 30 })
          Cookies.set("password", encrypt(this.loginForm.password), { expires: 30 })
          Cookies.set('rememberMe', this.loginForm.rememberMe, { expires: 30 })
        } else {
          Cookies.remove("username")
          Cookies.remove("password")
          Cookies.remove('rememberMe')
        }
        this.$store.dispatch("Login", this.loginForm).then(() => {
          this.$router.push({ path: resolvePostAuthPath(this.$route.query) }).catch(() => {})
        }).catch(() => {
          this.loading = false
          if (this.captchaEnabled) {
            this.getCode()
          }
        })
      })
    },
    handleGuestLogin() {
      if (this.guestLoading || this.loading) {
        return
      }
      this.guestLoading = true
      this.$store.dispatch('GuestLogin').then(() => {
        this.$router.push({ path: resolvePostAuthPath(this.$route.query) }).catch(() => {})
      }).catch(() => {
        this.guestLoading = false
      })
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import "~@/assets/styles/auth.scss";
</style>
