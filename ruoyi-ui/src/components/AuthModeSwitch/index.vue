<template>
  <nav class="auth-mode-switch" aria-label="登录或注册">
    <router-link
      class="auth-mode-switch__tab"
      :class="{ 'is-active': current === 'login' }"
      :to="loginTo"
      :aria-current="current === 'login' ? 'page' : null"
    >登录</router-link>
    <router-link
      v-if="registerEnabled"
      class="auth-mode-switch__tab"
      :class="{ 'is-active': current === 'register' }"
      :to="registerTo"
      :aria-current="current === 'register' ? 'page' : null"
    >注册</router-link>
  </nav>
</template>

<script>
export default {
  name: "AuthModeSwitch",
  props: {
    current: {
      type: String,
      required: true,
      validator: value => value === "login" || value === "register"
    },
    registerEnabled: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    loginTo() {
      return { path: "/login", query: this.$route.query }
    },
    registerTo() {
      return { path: "/register", query: this.$route.query }
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/assets/styles/tokens.scss";

.auth-mode-switch {
  display: flex;
  margin: 0 0 24px 0;
  padding: 4px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.06);
}

.auth-mode-switch__tab {
  flex: 1;
  height: 36px;
  line-height: 36px;
  text-align: center;
  border-radius: 8px;
  color: $color-auth-muted;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color $motion-fast ease, color $motion-fast ease;

  &:hover {
    color: #ffffff;
  }

  &:focus-visible {
    outline: 2px solid $color-ring;
    outline-offset: 2px;
  }

  &.is-active {
    background-color: $color-primary;
    color: $color-on-primary;
  }
}
</style>
