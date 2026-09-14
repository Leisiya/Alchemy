<template>
  <button
    v-if="visible"
    type="button"
    class="sidebar-collapse-toggle"
    :class="{ 'is-collapsed': !sidebar.opened }"
    :aria-label="label"
    :aria-expanded="sidebar.opened ? 'true' : 'false'"
    @click="toggleSidebar"
  >
    <i
      :class="sidebar.opened ? 'el-icon-arrow-left' : 'el-icon-arrow-right'"
      aria-hidden="true"
    />
  </button>
</template>

<script>
import { mapGetters } from 'vuex'
import productChrome from '@/utils/productChrome'

export default {
  name: 'SidebarCollapseToggle',
  computed: {
    ...mapGetters(['device', 'sidebar']),
    visible() {
      return this.device !== 'mobile' && !this.sidebar.hide
    },
    label() {
      return productChrome.sidebarCollapseLabel(this.sidebar.opened)
    }
  },
  methods: {
    toggleSidebar() {
      this.$store.dispatch('app/toggleSideBar')
    }
  }
}
</script>

<style lang="scss" scoped>
.sidebar-collapse-toggle {
  position: fixed;
  top: 72px;
  left: 164px;
  z-index: 1002;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  padding: 0;
  border: 1px solid var(--color-border, #E2E8F0);
  border-radius: 50%;
  background: #FFFFFF;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
  color: var(--color-foreground, #1A1F2E);
  cursor: pointer;
  transition: background-color 0.2s ease, left 0.28s ease;

  &:hover {
    background: #F8FAFC;
  }

  &:focus-visible {
    outline: 2px solid var(--color-ring, #15803D);
    outline-offset: 2px;
  }

  &.is-collapsed {
    left: 42px;
  }

  i {
    font-size: 12px;
    line-height: 1;
  }
}
</style>
