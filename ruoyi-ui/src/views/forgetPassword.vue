<template>
  <div class="auth-page">
    <el-form
      ref="resetForm"
      :model="form"
      :rules="resetRules"
      class="auth-form"
      hide-required-asterisk
      @submit.native.prevent="handleResetPwd"
    >
      <h1 class="auth-title">{{ title }}</h1>
      <p class="auth-subtitle">找回密码</p>
      <el-form-item prop="email">
        <el-input
          id="email"
          v-model="form.email"
          type="text"
          autocomplete="email"
          aria-label="请输入邮箱"
          placeholder="请输入邮箱"
        >
          <svg-icon slot="prefix" icon-class="user" class="el-input__icon input-icon" aria-hidden="true" />
        </el-input>
      </el-form-item>
      <el-form-item prop="newPassword" :rules="resetPwdValidator">
        <el-input
          id="newPassword"
          v-model="form.newPassword"
          type="password"
          autocomplete="new-password"
          aria-label="请输入新密码"
          placeholder="请输入新密码"
        >
          <svg-icon slot="prefix" icon-class="password" class="el-input__icon input-icon" aria-hidden="true" />
        </el-input>
      </el-form-item>
      <el-form-item prop="confirmPassword">
        <el-input
          id="confirmPassword"
          v-model="form.confirmPassword"
          type="password"
          autocomplete="new-password"
          aria-label="请再次输入新密码"
          placeholder="请再次输入新密码"
        >
          <svg-icon slot="prefix" icon-class="password" class="el-input__icon input-icon" aria-hidden="true" />
        </el-input>
      </el-form-item>
      <el-form-item prop="emailCode" class="auth-otp-item">
        <div class="auth-otp-row">
          <el-input
            id="emailCode"
            v-model="form.emailCode"
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
          <span v-if="!loading">重置密码</span>
          <span v-else>提交中...</span>
        </el-button>
        <div class="auth-back">
          <router-link class="auth-link" :to="{ path: '/login', query: $route.query }">返回登录</router-link>
        </div>
      </el-form-item>
    </el-form>
    <div class="auth-footer">
      <span>{{ footerContent }}</span>
    </div>
  </div>
</template>

<script>
import { sendResetPwdEmailCode, resetPwdByEmail } from "@/api/login"
import passwordRule from "@/utils/passwordRule"
import defaultSettings from '@/settings'
import { applyFormErrors } from '@/utils/authErrorSummary'
import { validateFormFields, FORGET_SEND_CODE_FIELDS } from '@/utils/validateFormFields'

export default {
  name: "ForgetPassword",
  mixins: [passwordRule],
  data() {
    return {
      title: process.env.VUE_APP_TITLE,
      footerContent: defaultSettings.footerContent,
      form: {
        email: "",
        emailCode: "",
        newPassword: "",
        confirmPassword: ""
      },
      loading: false,
      sendCodeLoading: false,
      countdown: 0,
      timer: null
    }
  },
  computed: {
    resetRules() {
      return {
        email: [
          { required: true, trigger: "blur", message: "请输入您的邮箱" },
          { type: "email", message: "请输入正确的邮箱地址", trigger: "blur" }
        ],
        emailCode: [{ required: true, trigger: "blur", message: "请输入验证码" }],
        confirmPassword: [
          { required: true, message: "请再次输入新密码", trigger: "blur" },
          {
            validator: (rule, value, callback) => {
              if (this.form.newPassword !== value) {
                callback(new Error("两次输入的密码不一致"))
              } else {
                callback()
              }
            }, trigger: "blur"
          }
        ]
      }
    },
    resetPwdValidator() {
      return this.registerPwdValidator
    }
  },
  watch: {
    "form.email"() {
      this.resetSendState()
    }
  },
  beforeDestroy() {
    this.clearTimer()
  },
  methods: {
    async handleSendCode() {
      if (this.countdown > 0 || this.sendCodeLoading) {
        return
      }
      const { valid, fields } = await validateFormFields(this.$refs.resetForm, FORGET_SEND_CODE_FIELDS)
      if (!applyFormErrors(this, valid, fields)) {
        return
      }
      this.sendCodeLoading = true
      this.doSendCode()
    },
    doSendCode() {
      sendResetPwdEmailCode(this.form.email).then(() => {
        this.sendCodeLoading = false
        this.startCountdown()
      }).catch(() => {
        this.sendCodeLoading = false
      })
    },
    resetSendState() {
      if (this.countdown === 0 && !this.form.emailCode) {
        return
      }
      this.clearTimer()
      this.countdown = 0
      this.form.emailCode = ""
    },
    handleResetPwd() {
      this.$refs.resetForm.validate((valid, fields) => {
        if (!applyFormErrors(this, valid, fields)) {
          return
        }
        this.loading = true
        resetPwdByEmail(this.form).then(() => {
          this.$alert("密码重置成功，请使用新密码登录", '系统提示', {
            type: 'success'
          }).then(() => {
            this.$router.push({ path: "/login", query: this.$route.query })
          }).catch(() => {})
        }).catch(() => {
          this.loading = false
        })
      })
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
