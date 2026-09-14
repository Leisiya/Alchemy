<template>
  <div v-if="visible" class="guest-banner" role="status">
    <p class="guest-banner__text">
      欢迎访客！您可以体验基本功能。
      <router-link class="guest-banner__link" to="/register">注册后解锁自选</router-link>
    </p>
    <button type="button" class="guest-banner__close" aria-label="关闭访客提示" @click="dismiss">
      <i class="el-icon-close" aria-hidden="true" />
    </button>
  </div>
</template>

<script>
const STORAGE_KEY = 'alchemy.guestBanner.dismissed'

export default {
  name: 'GuestBanner',
  computed: {
    visible() {
      return this.$store.getters.isGuest && !this.dismissed
    }
  },
  data() {
    return {
      dismissed: false
    }
  },
  created() {
    this.dismissed = sessionStorage.getItem(STORAGE_KEY) === '1'
  },
  methods: {
    dismiss() {
      this.dismissed = true
      sessionStorage.setItem(STORAGE_KEY, '1')
    }
  }
}
</script>

<style lang="scss" scoped>
.guest-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 16px 24px 0;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(21, 128, 61, 0.08);
  color: #1A1F2E;
  font-size: 13px;
}
.guest-banner__text { margin: 0; }
.guest-banner__link { color: #15803D; font-weight: 600; }
.guest-banner__close {
  border: 0;
  background: transparent;
  cursor: pointer;
  min-width: 32px;
  min-height: 32px;
  color: #475569;
}
.guest-banner__close:focus-visible {
  outline: 2px solid #15803D;
  outline-offset: 2px;
}
</style>
