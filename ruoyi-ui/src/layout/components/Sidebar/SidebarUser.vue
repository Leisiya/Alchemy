<template>
  <div
    class="sidebar-user"
    :class="['sidebar-user--' + placement, { 'is-collapse': collapse }]"
  >
    <el-dropdown
      trigger="click"
      :placement="dropdownPlacement"
      popper-class="sidebar-user-dropdown"
      @command="handleCommand"
    >
      <button type="button" class="sidebar-user__trigger" :aria-label="menuLabel">
        <user-letter-avatar size="sm" />
        <span v-if="!collapse" class="sidebar-user__name">{{ displayName }}</span>
      </button>
      <el-dropdown-menu slot="dropdown">
        <router-link v-if="isGuest" to="/register">
          <el-dropdown-item>立即注册</el-dropdown-item>
        </router-link>
        <router-link v-else to="/user/profile">
          <el-dropdown-item>个人中心</el-dropdown-item>
        </router-link>
        <el-dropdown-item divided command="logout">
          <span>退出登录</span>
        </el-dropdown-item>
      </el-dropdown-menu>
    </el-dropdown>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import productChrome from '@/utils/productChrome'
import UserLetterAvatar from '@/components/UserLetterAvatar'

export default {
  name: 'SidebarUser',
  components: { UserLetterAvatar },
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
    ...mapGetters(['nickName', 'name', 'isGuest']),
    displayName() {
      return (this.nickName || '').trim() || (this.name || '').trim() || '用户'
    },
    menuLabel() {
      return '用户菜单，' + this.displayName
    },
    dropdownPlacement() {
      return productChrome.dropdownPlacementFor(this.placement)
    }
  },
  methods: {
    handleCommand(command) {
      if (command === 'logout') {
        this.$store.dispatch('LogOut').then(() => {
          location.href = '/index'
        })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.sidebar-user {
  display: block;
  flex-shrink: 0;
  width: 100%;
  font-size: 14px;
  border-top: 1px solid var(--color-border, #E2E8F0);
  padding: 12px 16px;
  box-sizing: border-box;
}

.sidebar-user >>> .el-dropdown {
  display: block;
  width: 100%;
}

.sidebar-user--navbar {
  border-top: 0;
  width: auto;
  padding: 0 16px 0 8px;
}

.sidebar-user.is-collapse {
  padding: 12px 0;
}

.sidebar-user__trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-height: 44px;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  color: inherit;
  text-align: left;
}

.sidebar-user.is-collapse .sidebar-user__trigger {
  justify-content: center;
}

.sidebar-user__trigger:hover ::v-deep .user-letter-avatar {
  background: var(--color-primary-hover, #166534);
}

.sidebar-user__trigger:focus-visible {
  outline: 2px solid var(--color-ring, #15803D);
  outline-offset: 2px;
}

.sidebar-user__name {
  min-width: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-foreground, #1A1F2E);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

<style lang="scss">
.sidebar-user-dropdown.el-popper[x-placement^="top"] {
  margin-bottom: 8px;
}
</style>
