<template>
  <el-drawer
    title="通知中心"
    :visible="drawerVisible"
    direction="rtl"
    :size="drawerSize"
    custom-class="notice-drawer"
    :wrapper-closable="true"
    @close="handleClose"
  >
    <div
      class="notice-drawer__body"
      :aria-busy="loading ? 'true' : 'false'"
    >
      <div v-if="!activeItem" class="notice-drawer__toolbar">
        <span class="notice-drawer__unread">{{ unreadText }}</span>
        <button
          type="button"
          class="notice-drawer__mark-all"
          :disabled="!unreadCount"
          @click="markAll"
        >
          全部已读
        </button>
      </div>

      <div v-if="loading" class="notice-drawer__status">加载中…</div>
      <div v-else-if="error" class="notice-drawer__status">加载失败</div>

      <template v-else-if="activeItem">
        <button type="button" class="notice-drawer__back" @click="backToList">
          返回
        </button>
        <h2 class="notice-drawer__title">{{ activeItem.noticeTitle }}</h2>
        <p class="notice-drawer__time">{{ parseTime(activeItem.createTime) }}</p>
        <div class="notice-drawer__content" v-html="activeItem.noticeContent" />
      </template>

      <div v-else-if="!list.length" class="notice-drawer__empty">暂无通知</div>

      <ul v-else class="notice-drawer__list">
        <li v-for="item in list" :key="item.noticeId">
          <button
            type="button"
            class="notice-drawer__row"
            @click="openItem(item.noticeId)"
          >
            <span v-if="!item.isRead" class="notice-drawer__dot" aria-hidden="true" />
            <span v-else class="notice-drawer__dot-spacer" aria-hidden="true" />
            <span class="notice-drawer__row-main">
              <span class="notice-drawer__row-top">
                <span class="notice-drawer__type">{{ typeLabel(item.noticeType) }}</span>
                <span class="notice-drawer__relative">{{ relative(item.createTime) }}</span>
              </span>
              <span class="notice-drawer__row-title">{{ item.noticeTitle }}</span>
              <span class="notice-drawer__preview">{{ preview(item.noticeContent) }}</span>
            </span>
          </button>
        </li>
      </ul>
    </div>
  </el-drawer>
</template>

<script>
import { mapGetters, mapState } from 'vuex'
import noticeInbox from '@/utils/noticeInbox'

export default {
  name: 'NoticeDrawer',
  computed: {
    ...mapGetters(['device']),
    ...mapState('notice', ['drawerVisible', 'list', 'activeId', 'loading', 'error', 'unreadCount']),
    drawerSize() {
      return this.device === 'mobile' ? '100%' : '400px'
    },
    activeItem() {
      if (this.activeId == null || this.activeId === '') {
        return null
      }
      return this.list.find(item => Number(item.noticeId) === Number(this.activeId)) || null
    },
    unreadText() {
      if (!this.unreadCount) {
        return '暂无未读'
      }
      return this.unreadCount + ' 条未读'
    }
  },
  methods: {
    handleClose() {
      this.$store.dispatch('notice/closeDrawer')
    },
    markAll() {
      this.$store.dispatch('notice/markAll')
    },
    openItem(noticeId) {
      this.$store.dispatch('notice/openItem', noticeId)
    },
    backToList() {
      this.$store.commit('notice/SET_ACTIVE_ID', null)
    },
    typeLabel(type) {
      if (type === '1') {
        return '通知'
      }
      if (type === '2') {
        return '公告'
      }
      return type || ''
    },
    relative(time) {
      return noticeInbox.relativeTime(time, new Date())
    },
    preview(html) {
      return noticeInbox.stripHtmlPreview(html)
    }
  }
}
</script>

<style lang="scss">
.notice-drawer {
  color: var(--color-foreground, #1A1F2E);

  .el-drawer__header {
    margin-bottom: 8px;
    padding: 16px 16px 0;
    color: var(--color-foreground, #1A1F2E);
    font-weight: 600;
  }

  .el-drawer__body {
    padding: 0 16px 16px;
  }
}

.notice-drawer__body {
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
}

.notice-drawer__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 12px;
}

.notice-drawer__unread {
  font-size: 12px;
  color: var(--color-muted-foreground, #475569);
}

.notice-drawer__mark-all,
.notice-drawer__back {
  border: 0;
  background: transparent;
  padding: 4px 8px;
  border-radius: var(--radius-md, 8px);
  color: var(--color-primary, #15803D);
  font-size: 13px;
  cursor: pointer;

  &:hover:not(:disabled) {
    background: rgba(21, 128, 61, 0.08);
  }

  &:disabled {
    color: var(--color-muted-foreground, #475569);
    cursor: default;
  }

  &:focus-visible {
    outline: 2px solid var(--color-ring, #15803D);
    outline-offset: 2px;
  }
}

.notice-drawer__status,
.notice-drawer__empty {
  padding: 48px 8px;
  text-align: center;
  color: var(--color-muted-foreground, #475569);
  font-size: 14px;
}

.notice-drawer__title {
  margin: 8px 0 4px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-foreground, #1A1F2E);
}

.notice-drawer__time {
  margin: 0 0 16px;
  font-size: 12px;
  color: var(--color-muted-foreground, #475569);
}

.notice-drawer__content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-foreground, #1A1F2E);
  word-break: break-word;
}

.notice-drawer__list {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow: auto;
}

.notice-drawer__row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
  padding: 12px 8px;
  border: 0;
  border-radius: var(--radius-md, 8px);
  background: transparent;
  text-align: left;
  cursor: pointer;
  color: inherit;

  &:hover {
    background: var(--color-muted, #E2E8F0);
  }

  &:focus-visible {
    outline: 2px solid var(--color-ring, #15803D);
    outline-offset: 2px;
  }
}

.notice-drawer__dot,
.notice-drawer__dot-spacer {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  margin-top: 6px;
  border-radius: 50%;
}

.notice-drawer__dot {
  background: var(--color-primary, #15803D);
}

.notice-drawer__row-main {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.notice-drawer__row-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.notice-drawer__type,
.notice-drawer__relative,
.notice-drawer__preview {
  font-size: 12px;
  color: var(--color-muted-foreground, #475569);
}

.notice-drawer__row-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-foreground, #1A1F2E);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notice-drawer__preview {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (prefers-reduced-motion: reduce) {
  .notice-drawer__row,
  .notice-drawer__mark-all,
  .notice-drawer__back {
    transition: none;
  }
}
</style>
