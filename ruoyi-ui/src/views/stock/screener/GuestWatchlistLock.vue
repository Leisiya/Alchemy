<template>
  <div class="guest-watchlist-lock" role="status">
    <i class="el-icon-lock guest-watchlist-lock__icon" aria-hidden="true" />
    <h2 id="guest-watchlist-lock-title" class="guest-watchlist-lock__title">自选功能需要注册</h2>
    <p class="guest-watchlist-lock__lead">访客无法使用自选。注册完整账号后可享受：</p>
    <ul class="guest-watchlist-lock__list">
      <li><i class="el-icon-check" aria-hidden="true" />云端保存自选</li>
      <li><i class="el-icon-check" aria-hidden="true" />最多 200 只</li>
      <li><i class="el-icon-check" aria-hidden="true" />在列表用星标随时加减</li>
    </ul>
    <el-button type="primary" class="guest-watchlist-lock__cta" @click="goRegister">立即注册完整账号</el-button>
  </div>
</template>

<script>
export default {
  name: "GuestWatchlistLock",
  methods: {
    goRegister() {
      this.$router.push("/register")
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/assets/styles/tokens.scss";

.guest-watchlist-lock {
  width: 420px;
  max-width: 100%;
  margin: $space-3xl auto $space-2xl;
  padding: $space-3xl $space-2xl $space-2xl;
  background: $color-card;
  border: 1px solid $color-border;
  border-radius: $radius-lg;
  box-shadow: $shadow-card;
  text-align: center;
}

.guest-watchlist-lock__icon {
  display: block;
  margin: 0 auto $space-xl;
  font-size: 48px;
  color: $color-primary;
}

.guest-watchlist-lock__title {
  margin: 0 0 $space-md;
  font-size: $font-title;
  font-weight: 700;
  line-height: 1.3;
  color: $color-foreground;
}

.guest-watchlist-lock__lead {
  margin: 0 0 $space-xl;
  font-size: $font-body;
  line-height: 1.5;
  color: $color-muted-foreground;
}

.guest-watchlist-lock__list {
  margin: 0 0 $space-2xl;
  padding: 0;
  list-style: none;
  text-align: left;
  font-size: $font-body;
  color: $color-foreground;

  li {
    display: flex;
    align-items: center;
    gap: $space-md;
    margin: 0 0 $space-lg;
  }

  .el-icon-check {
    color: $color-primary;
  }
}

.guest-watchlist-lock__cta {
  width: 100%;
  background: $color-primary;
  border-color: $color-primary;
}

.guest-watchlist-lock__cta:focus-visible {
  outline: 2px solid $color-ring;
  outline-offset: 2px;
}
</style>
