<template>
  <transition name="bookmark-tip">
    <aside
      v-if="visible && device !== 'mobile'"
      class="bookmark-tip"
      role="dialog"
      aria-labelledby="bookmark-tip-title"
      aria-describedby="bookmark-tip-description"
    >
      <div class="bookmark-tip__icon">
        <svg-icon icon-class="star" aria-hidden="true" />
      </div>

      <button
        type="button"
        class="bookmark-tip__close"
        aria-label="关闭收藏提示"
        @click="dismiss"
      >
        <i class="el-icon-close" aria-hidden="true" />
      </button>

      <div class="bookmark-tip__content">
        <h2 id="bookmark-tip-title" class="bookmark-tip__title">收藏本站</h2>
        <p id="bookmark-tip-description" class="bookmark-tip__description">
          按 {{ shortcut }} 收藏本站，方便下次访问
        </p>
        <div class="bookmark-tip__actions">
          <label class="bookmark-tip__checkbox">
            <input v-model="dontShowAgain" type="checkbox">
            <span>不再提示</span>
          </label>
          <button type="button" class="bookmark-tip__confirm" @click="dismiss">知道了</button>
        </div>
      </div>
    </aside>
  </transition>
</template>

<script>
import {
  shortcutHint,
  shouldShowBookmarkTip,
  readDismissed,
  persistDismiss
} from '@/utils/bookmarkTip'

export default {
  name: 'BookmarkTip',
  data() {
    return {
      visible: false,
      dontShowAgain: false,
      showTimer: null,
      shortcut: shortcutHint(navigator.userAgent, navigator.platform)
    }
  },
  computed: {
    device() {
      return this.$store.state.app.device
    }
  },
  watch: {
    device(value) {
      if (value === 'mobile') {
        this.clearShowTimer()
        return
      }
      this.scheduleShow()
    }
  },
  created() {
    this.scheduleShow()
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeydown)
  },
  beforeDestroy() {
    this.clearShowTimer()
    window.removeEventListener('keydown', this.handleKeydown)
  },
  methods: {
    scheduleShow() {
      const dismissed = readDismissed(this.$cache.local, this.$cache.session)
      if (
        !shouldShowBookmarkTip({ ...dismissed, device: this.device }) ||
        this.visible ||
        this.showTimer !== null
      ) {
        return
      }
      this.showTimer = window.setTimeout(() => {
        if (this.device !== 'mobile') {
          this.visible = true
        }
        this.showTimer = null
      }, 1200)
    },
    clearShowTimer() {
      if (this.showTimer !== null) {
        window.clearTimeout(this.showTimer)
        this.showTimer = null
      }
    },
    handleKeydown(event) {
      if (event.key === 'Escape' && this.visible && this.device !== 'mobile') {
        this.dismiss()
      }
    },
    dismiss() {
      persistDismiss({
        dontShowAgain: this.dontShowAgain,
        localStore: this.$cache.local,
        sessionStore: this.$cache.session
      })
      this.visible = false
    }
  }
}
</script>

<style lang="scss" scoped>
.bookmark-tip {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1002;
  display: flex;
  width: 320px;
  max-width: calc(100vw - 32px);
  padding: 20px 16px;
  color: #fff;
  background: linear-gradient(90deg, #F59E0B 0%, #EA580C 100%);
  border-radius: 12px;
  box-shadow: 0 12px 30px rgba(124, 45, 18, 0.24);
}

.bookmark-tip__icon {
  display: flex;
  flex: 0 0 40px;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  margin-right: 12px;
  font-size: 20px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.bookmark-tip__content {
  min-width: 0;
  padding-right: 20px;
}

.bookmark-tip__title {
  margin: 0 0 5px;
  color: #fff;
  font-size: 16px;
  line-height: 24px;
}

.bookmark-tip__description {
  margin: 0;
  color: #fff;
  font-size: 13px;
  line-height: 20px;
}

.bookmark-tip__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
  gap: 12px;
}

.bookmark-tip__checkbox {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #fff;
  font-size: 13px;
  cursor: pointer;

  input {
    margin: 0;
  }
}

.bookmark-tip__confirm {
  min-height: 32px;
  padding: 6px 14px;
  color: #EA580C;
  font-weight: 600;
  background: #fff;
  border: 0;
  border-radius: 6px;
  cursor: pointer;
}

.bookmark-tip__close {
  position: absolute;
  top: 8px;
  right: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  color: #fff;
  font-size: 16px;
  background: transparent;
  border: 0;
  border-radius: 6px;
  cursor: pointer;
}

.bookmark-tip-enter-active {
  transition: opacity 200ms ease, transform 200ms ease;
}

.bookmark-tip-enter {
  opacity: 0;
  transform: translateY(12px);
}

@media (prefers-reduced-motion: reduce) {
  .bookmark-tip-enter-active {
    transition: none;
  }
}
</style>
