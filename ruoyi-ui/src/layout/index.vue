<template>
  <div :class="classObj" class="app-wrapper" :style="{'--current-color': theme, '--current-color-light': theme + '1a', '--current-color-dark-bg': theme + '33'}">
    <div v-if="device==='mobile'&&sidebar.opened" class="drawer-bg" @click="handleClickOutside"/>
    <sidebar v-if="!sidebar.hide" class="sidebar-container"/>
    <sidebar-collapse-toggle/>
    <div :class="{hasTagsView:needTagsView,sidebarHide:sidebar.hide,hasNavbar:needNavbar}" class="main-container">
      <div v-if="needNavbar" :class="{'fixed-header':fixedHeader}">
        <navbar/>
        <tags-view v-if="needTagsView"/>
      </div>
      <guest-banner/>
      <app-main/>
    </div>
    <bookmark-tip/>
    <notice-drawer/>
  </div>
</template>

<script>
import { AppMain, BookmarkTip, GuestBanner, Navbar, NoticeDrawer, Sidebar, TagsView } from './components'
import SidebarCollapseToggle from './components/Sidebar/SidebarCollapseToggle'
import ResizeMixin from './mixin/ResizeHandler'
import { mapState } from 'vuex'
import variables from '@/assets/styles/variables.scss'
import noticeInbox from '@/utils/noticeInbox'

export default {
  name: 'Layout',
  components: {
    AppMain,
    BookmarkTip,
    GuestBanner,
    Navbar,
    NoticeDrawer,
    Sidebar,
    SidebarCollapseToggle,
    TagsView
  },
  mixins: [ResizeMixin],
  computed: {
    ...mapState({
      theme: state => state.settings.theme,
      sideTheme: state => state.settings.sideTheme,
      sidebar: state => state.app.sidebar,
      device: state => state.app.device,
      needTagsView: state => state.settings.tagsView,
      fixedHeader: state => state.settings.fixedHeader,
      navType: state => state.settings.navType
    }),
    needNavbar() {
      return this.device === 'mobile' || this.sidebar.hide || this.navType !== 1
    },
    classObj() {
      return {
        hideSidebar: !this.sidebar.opened,
        openSidebar: this.sidebar.opened,
        withoutAnimation: this.sidebar.withoutAnimation,
        mobile: this.device === 'mobile'
      }
    },
    variables() {
      return variables
    }
  },
  created() {
    this.$store.dispatch('notice/fetchUnread')
    this.noticePollTimer = setInterval(() => {
      this.$store.dispatch('notice/fetchUnread')
    }, noticeInbox.POLL_MS)
  },
  beforeDestroy() {
    if (this.noticePollTimer) {
      clearInterval(this.noticePollTimer)
      this.noticePollTimer = null
    }
  },
  methods: {
    handleClickOutside() {
      this.$store.dispatch('app/closeSideBar', { withoutAnimation: false })
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "~@/assets/styles/mixin.scss";
  @import "~@/assets/styles/variables.scss";

  .app-wrapper {
    @include clearfix;
    position: relative;
    height: 100%;
    width: 100%;

    &.mobile.openSidebar {
      position: fixed;
      top: 0;
    }
  }

  .main-container {
    height: 100vh;
    overflow: hidden;
  }

  .drawer-bg {
    background: #000;
    opacity: 0.3;
    width: 100%;
    top: 0;
    height: 100%;
    position: absolute;
    z-index: 999;
  }

  .fixed-header {
    position: fixed;
    top: 0;
    right: 0;
    z-index: 9;
    width: calc(100% - #{$base-sidebar-width});
    transition: width 0.28s;
  }

  .hideSidebar .fixed-header {
    width: calc(100% - 54px);
  }

  .sidebarHide .fixed-header {
    width: 100%;
  }

  .mobile .fixed-header {
    width: 100%;
  }
</style>
