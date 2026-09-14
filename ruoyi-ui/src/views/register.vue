<template>
  <div class="auth-page">
    <el-form
      ref="registerForm"
      :model="registerForm"
      :rules="registerRules"
      class="auth-form"
      hide-required-asterisk
      @submit.native.prevent="handleRegister"
    >
      <h1 class="auth-title">{{ title }}</h1>
      <p class="auth-subtitle">A股价值投资好助手</p>
      <auth-mode-switch current="register" :register-enabled="registerEnabled" />
      <el-form-item prop="email">
        <el-input
          id="email"
          v-model="registerForm.email"
          type="text"
          autocomplete="email"
          aria-label="请输入邮箱"
          placeholder="请输入邮箱"
        >
          <svg-icon slot="prefix" icon-class="user" class="el-input__icon input-icon" aria-hidden="true" />
        </el-input>
      </el-form-item>
      <el-form-item prop="password" :rules="registerPwdValidator">
        <el-input
          id="password"
          v-model="registerForm.password"
          type="password"
          autocomplete="new-password"
          aria-label="请输入密码"
          placeholder="请输入密码"
        >
          <svg-icon slot="prefix" icon-class="password" class="el-input__icon input-icon" aria-hidden="true" />
        </el-input>
      </el-form-item>
      <el-form-item prop="confirmPassword">
        <el-input
          id="confirmPassword"
          v-model="registerForm.confirmPassword"
          type="password"
          autocomplete="new-password"
          aria-label="请再次输入密码"
          placeholder="请再次输入密码"
        >
          <svg-icon slot="prefix" icon-class="password" class="el-input__icon input-icon" aria-hidden="true" />
        </el-input>
      </el-form-item>
      <el-form-item prop="code" v-if="captchaEnabled">
        <el-input
          id="code"
          v-model="registerForm.code"
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
      <el-form-item prop="emailCode" class="auth-otp-item">
        <div class="auth-otp-row">
          <el-input
            id="emailCode"
            v-model="registerForm.emailCode"
            autocomplete="one-time-code"
            aria-label="请输入验证码"
            placeholder="请输入验证码"
          >
            <svg-icon slot="prefix" icon-class="validCode" class="el-input__icon input-icon" aria-hidden="true" />
          </el-input>
          <button
            type="button"
            class="auth-send-code"
            :disabled="countdown > 0 || sendCodeLoading"
            @click="handleSendCode"
          >
            <span v-if="sendCodeLoading">发送中...</span>
            <span v-else-if="countdown > 0">重新发送({{ countdown }}s)</span>
            <span v-else>发送验证码</span>
          </button>
        </div>
      </el-form-item>
      <el-form-item style="width:100%;">
        <el-button
          :loading="loading"
          size="medium"
          type="primary"
          native-type="submit"
          style="width:100%;"
        >
          <span v-if="entering">正在进入...</span>
          <span v-else-if="loading">注册中...</span>
          <span v-else>注册</span>
        </el-button>
      </el-form-item>
    </el-form>
    <div class="auth-footer">
      <span>{{ footerContent }}</span>
    </div>
  </div>
</template>

<script>
import { getCodeImg, sendEmailCode, register } from "@/api/login"
import passwordRule from "@/utils/passwordRule"
import defaultSettings from '@/settings'
import { applyFormErrors } from '@/utils/authErrorSummary'
import { validateFormFields, REGISTER_SEND_CODE_FIELDS } from '@/utils/validateFormFields'
import AuthModeSwitch from '@/components/AuthModeSwitch'
import { resolvePostAuthPath } from '@/utils/authRedirect'

export default {
  name: "Register",
  components: { AuthModeSwitch },
  mixins: [passwordRule],
  data() {
    return {
      title: process.env.VUE_APP_TITLE,
      footerContent: defaultSettings.footerContent,
      codeUrl: "",
      registerForm: {
        email: "",
        password: "",
        confirmPassword: "",
        code: "",
        uuid: "",
        emailCode: ""
      },
      loading: false,
      entering: false,
      sendCodeLoading: false,
      captchaEnabled: false,
      registerEnabled: true,
      countdown: 0,
      timer: null
    }
  },
  computed: {
    registerRules() {
      return {
        email: [
          { required: true, trigger: "blur", message: "请输入您的邮箱" },
          { type: "email", message: "请输入正确的邮箱地址", trigger: "blur" }
        ],
        confirmPassword: [
          { required: true, message: "请再次输入您的密码", trigger: "blur" },
          {
            validator: (rule, value, callback) => {
              if (this.registerForm.password !== value) {
                callback(new Error("两次输入的密码不一致"))
              } else {
                callback()
              }
            }, trigger: "blur"
          }
        ],
        code: [{ required: true, trigger: "change", message: "请输入验证码" }],
        emailCode: [{ required: true, trigger: "blur", message: "请输入验证码" }]
      }
    }
  },
  watch: {
    "registerForm.email"() {
      this.resetSendState()
    }
  },
  created() {
    this.getCode()
  },
  beforeDestroy() {
    this.clearTimer()
  },
  methods: {
    getCode() {
      getCodeImg().then(res => {
        this.captchaEnabled = res.captchaEnabled === true
        this.registerEnabled = res.registerEnabled !== false
        if (this.captchaEnabled) {
          this.codeUrl = "data:image/gif;base64," + res.img
          this.registerForm.uuid = res.uuid
        }
      })
    },
    resetSendState() {
      if (this.countdown === 0 && !this.registerForm.emailCode) {
        return
      }
      this.clearTimer()
      this.countdown = 0
      this.registerForm.emailCode = ""
    },
    async handleSendCode() {
      if (this.countdown > 0 || this.sendCodeLoading) {
        return
      }
      const { valid, fields } = await validateFormFields(this.$refs.registerForm, REGISTER_SEND_CODE_FIELDS)
      if (!applyFormErrors(this, valid, fields)) {
        return
      }
      this.sendCodeLoading = true
      this.doSendCode()
    },
    doSendCode() {
      sendEmailCode(this.registerForm.email).then(() => {
        this.sendCodeLoading = false
        this.startCountdown()
      }).catch(() => {
        this.sendCodeLoading = false
      })
    },
    handleRegister() {
      this.$refs.registerForm.validate((valid, fields) => {
        if (!applyFormErrors(this, valid, fields)) {
          return
        }
        this.loading = true
        register(this.registerForm).then(res => {
          this.entering = true
          if (!res.token && this.captchaEnabled) {
            this.loading = false
            this.entering = false
            this.$modal.msgSuccess("注册成功，请登录")
            this.$router.push({ path: "/login", query: this.$route.query }).catch(() => {})
            return
          }
          const session = res.token
            ? this.$store.dispatch("ApplyToken", res.token)
            : this.$store.dispatch("Login", {
              username: this.registerForm.email,
              password: this.registerForm.password,
              code: this.registerForm.code,
              uuid: this.registerForm.uuid
            })
          return session.then(() => this.enterApp()).catch(() => {
            this.loading = false
            this.entering = false
            this.$modal.msgSuccess("注册成功，请登录")
            this.$router.push({ path: "/login", query: this.$route.query }).catch(() => {})
          })
        }).catch(() => {
          this.loading = false
          this.entering = false
          if (this.captchaEnabled) {
            this.getCode()
          }
        })
      })
    },
    enterApp() {
      this.$modal.msgSuccess("注册成功")
      this.$router.push({ path: resolvePostAuthPath(this.$route.query) }).catch(() => {})
    },
    startCountdown() {
      this.countdown = 60
      this.clearTimer()
      this.timer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          this.clearTimer()
        }
      }, 1000)
    },
    clearTimer() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import "~@/assets/styles/auth.scss";
</style>
