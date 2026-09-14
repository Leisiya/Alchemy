<template>
  <div
    class="notice-center-entry"
    :class="['notice-center-entry--' + placement, { 'is-collapse': collapse }]"
  >
    <button
      type="button"
      class="notice-center-entry__button"
      :aria-label="badgeLabel"
      :aria-expanded="drawerVisible ? 'true' : 'false'"
      @click="toggleDrawer"
    >
      <el-badge :value="unreadCount" :hidden="!unreadCount" :max="99">
        <svg-icon icon-class="bell" aria-hidden="true" />
      </el-badge>
      <span v-if="!collapse" class="notice-center-entry__label">通知中心</span>
    </button>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import noticeInbox from '@/utils/noticeInbox'

export default {
  name: 'NoticeCenterEntry',
  props: {
    collapse: {
      type: Boolean,
      default: false
    },
    placement: {
      type: String,
      default: 'sidebar'
    }
  },
  computed: {
    ...mapState('notice', ['unreadCount', 'drawerVisible']),
    badgeLabel() {
      return noticeInbox.unreadBadgeLabel(this.unreadCount)
    }
  },
  methods: {
    toggleDrawer() {
      if (this.drawerVisible) {
        this.$store.dispatch('notice/closeDrawer')
      } else {
        this.$store.dispatch('notice/openDrawer')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.notice-center-entry {
  display: block;
  flex-shrink: 0;
  width: 100%;
  font-size: 14px;
  border-top: 1px solid var(--color-border, #E2E8F0);
  padding: 8px 16px;
  box-sizing: border-box;
}

.notice-center-entry--navbar {
  border-top: 0;
  width: auto;
  padding: 0 8px;
  overflow: visible;
}

.notice-center-entry.is-collapse {
  padding: 8px 0;
}

.notice-center-entry--navbar.is-collapse {
  padding: 0 8px;
  overflow: visible;
}

.notice-center-entry__button {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-height: 44px;
  padding: 0 8px;
  border: 0;
  border-radius: var(--radius-md, 8px);
  background: transparent;
  cursor: pointer;
  color: inherit;
  text-align: left;

  &:hover {
    background: rgba(0, 0, 0, 0.04);
  }

  &:focus-visible {
    outline: 2px solid var(--color-ring, #15803D);
    outline-offset: 2px;
  }
}

.notice-center-entry.is-collapse .notice-center-entry__button {
  justify-content: center;
  padding: 0;
}

.notice-center-entry.is-collapse >>> .svg-icon {
  margin-right: 0 !important;
}

.notice-center-entry__label {
  min-width: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-foreground, #1A1F2E);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.theme-dark .notice-center-entry:not(.notice-center-entry--navbar) .notice-center-entry__label {
  color: #fff;
}

.notice-center-entry--navbar .notice-center-entry__button {
  width: auto;
  min-width: 44px;
  min-height: 44px;
  justify-content: center;
}

@media (prefers-reduced-motion: reduce) {
  .notice-center-entry__button {
    transition: none;
  }
}
</style>
