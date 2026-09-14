<template>
  <div class="navbar" :class="'nav' + navType">
    <hamburger
      v-if="device==='mobile'"
      id="hamburger-container"
      :is-active="sidebar.opened"
      class="hamburger-container"
      @toggleClick="toggleSideBar"
    />
    <notice-center-entry
      v-if="device==='mobile'"
      placement="navbar"
      :collapse="true"
    />

    <top-nav v-if="navType == 2" id="topmenu-container" class="topmenu-container" />
    <template v-if="navType == 3">
      <logo v-show="showLogo" :collapse="false"></logo>
      <top-bar id="topbar-container" class="topbar-container" />
    </template>
    <div v-if="sidebar.hide" class="right-menu">
      <sidebar-user placement="navbar" :collapse="false" />
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import TopNav from './TopNav'
import TopBar from './TopBar'
import Logo from './Sidebar/Logo'
import SidebarUser from './Sidebar/SidebarUser'
import Hamburger from '@/components/Hamburger'
import NoticeCenterEntry from './NoticeCenterEntry'
export default {
  components: {
    Logo,
    TopNav,
    TopBar,
    Hamburger,
    SidebarUser,
    NoticeCenterEntry
  },
  computed: {
    ...mapGetters([
      'sidebar',
      'device'
    ]),
    navType: {
      get() {
        return this.$store.state.settings.navType
      }
    },
    showLogo: {
      get() {
        return this.$store.state.settings.sidebarLogo
      }
    }
  },
  methods: {
    toggleSideBar() {
      this.$store.dispatch('app/toggleSideBar')
    }
  }
}
</script>

<style lang="scss" scoped>
.navbar.nav3 {
  .hamburger-container {
    display: none !important;
  }
}

.navbar {
  height: 50px;
  overflow: visible;
  position: relative;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  align-items: center;
  box-sizing: border-box;

  .hamburger-container {
    line-height: 46px;
    height: 100%;
    cursor: pointer;
    transition: background .3s;
    -webkit-tap-highlight-color:transparent;
    display: flex;
    align-items: center;
    flex-shrink: 0;
    margin-right: 8px;

    &:hover {
      background: rgba(0, 0, 0, .025)
    }
  }

  .topmenu-container {
    position: absolute;
    left: 50px;
  }

  .topbar-container {
    flex: 1;
    min-width: 0;
    display: flex;
    align-items: center;
    overflow: hidden;
    margin-left: 8px;
  }

  .right-menu {
    height: 100%;
    line-height: 50px;
    display: flex;
    align-items: center;
    margin-left: auto;

    &:focus-visible {
      outline: 2px solid var(--color-ring, #15803D);
      outline-offset: 2px;
    }
  }
}

@media (prefers-reduced-motion: reduce) {
  .navbar .hamburger-container {
    transition: none;
  }
}
</style>
