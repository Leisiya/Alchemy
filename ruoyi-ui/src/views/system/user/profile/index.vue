<template>
  <div class="app-container profile-page">
    <header class="profile-header">
      <h1 class="profile-title">个人中心</h1>
      <p class="profile-subtitle">查看账号信息，管理登录密码</p>
    </header>
    <div class="profile-grid">
      <section class="profile-card identity-card" aria-labelledby="profile-identity-heading">
        <div class="identity-card__cover" aria-hidden="true"></div>
        <div class="identity-card__hero">
          <user-letter-avatar size="lg" class="identity-card__avatar" />
          <h2 id="profile-identity-heading" class="profile-name">{{ displayName }}</h2>
          <p v-if="roleText" class="profile-role">{{ roleText }}</p>
        </div>
        <dl class="profile-fields">
          <div v-if="showNickName" class="profile-field">
            <span class="profile-field__icon" aria-hidden="true"><svg-icon icon-class="people" /></span>
            <dt>昵称</dt>
            <dd>{{ nickNameText }}</dd>
          </div>
          <div class="profile-field">
            <span class="profile-field__icon" aria-hidden="true"><svg-icon icon-class="user" /></span>
            <dt>用户名称</dt>
            <dd>{{ user.userName || '—' }}</dd>
          </div>
          <div class="profile-field">
            <span class="profile-field__icon" aria-hidden="true"><svg-icon icon-class="email" /></span>
            <dt>用户邮箱</dt>
            <dd>{{ user.email || '—' }}</dd>
          </div>
          <div class="profile-field">
            <span class="profile-field__icon" aria-hidden="true"><svg-icon icon-class="date" /></span>
            <dt>创建日期</dt>
            <dd>{{ user.createTime || '—' }}</dd>
          </div>
        </dl>
      </section>
      <section class="profile-card password-card" aria-labelledby="profile-password-heading">
        <header class="password-card__header">
          <span class="password-card__icon" aria-hidden="true"><svg-icon icon-class="password" /></span>
          <div class="password-card__heading">
            <h2 id="profile-password-heading" class="profile-card-title">修改密码</h2>
            <p class="password-card__desc">定期更换密码，保障账号安全</p>
          </div>
        </header>
        <div class="password-card__body">
          <resetPwd />
          <aside class="pwd-tips" aria-labelledby="pwd-tips-heading">
            <h3 id="pwd-tips-heading" class="pwd-tips__title">安全建议</h3>
            <ul class="pwd-tips__list">
              <li>避免使用生日、手机号等容易被猜到的信息</li>
              <li>不要与其他平台使用相同的密码</li>
              <li>建议每隔一段时间更换一次密码</li>
            </ul>
          </aside>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import UserLetterAvatar from '@/components/UserLetterAvatar'
import resetPwd from './resetPwd'
import { getUserProfile } from '@/api/system/user'

export default {
  name: 'Profile',
  components: { UserLetterAvatar, resetPwd },
  data() {
    return {
      user: {},
      roleGroup: ''
    }
  },
  computed: {
    nickNameText() {
      return (this.user.nickName || '').trim()
    },
    userNameText() {
      return (this.user.userName || '').trim()
    },
    displayName() {
      return this.nickNameText || this.userNameText || '用户'
    },
    showNickName() {
      return this.nickNameText !== '' && this.nickNameText !== this.userNameText
    },
    roleText() {
      if (this.roleGroup == null) {
        return ''
      }
      return String(this.roleGroup).trim()
    }
  },
  created() {
    this.getUser()
  },
  methods: {
    getUser() {
      getUserProfile().then(response => {
        this.user = response.data || {}
        this.roleGroup = response.roleGroup || ''
      })
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/assets/styles/tokens.scss";

.profile-page {
  background: $color-background;
  min-height: calc(100vh - 84px);
  padding: $space-2xl;
}

.profile-header {
  max-width: 1200px;
  margin: 0 0 $space-2xl;
}

.profile-title {
  margin: 0;
  font-size: $font-title;
  font-weight: 700;
  line-height: 1.2;
  color: $color-foreground;
}

.profile-subtitle {
  margin: $space-sm 0 0;
  font-size: $font-num;
  color: $color-muted-foreground;
}

.profile-grid {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: $space-2xl;
  align-items: start;
  max-width: 1200px;
}

.profile-card {
  background: $color-card;
  border-radius: $radius-lg;
  box-shadow: $shadow-card;
  animation: profile-rise $motion-base ease-out both;
}

.password-card {
  padding: $space-2xl;
  animation-delay: 60ms;
}

.identity-card {
  overflow: hidden;
}

.identity-card__cover {
  height: 96px;
  background:
    radial-gradient(circle at 85% 15%, rgba(255, 255, 255, 0.16), transparent 45%),
    radial-gradient(circle at 12% 90%, rgba(255, 255, 255, 0.08), transparent 40%),
    linear-gradient(120deg, #166534 0%, $color-primary 52%, #1D9A51 100%);
}

.identity-card__hero {
  margin-top: -40px;
  padding: 0 $space-2xl $space-xl;
  text-align: center;
}

.identity-card__avatar {
  box-shadow: 0 0 0 4px $color-card;
}

.profile-name {
  margin: $space-lg 0 0;
  font-size: 18px;
  font-weight: 700;
  line-height: 1.3;
  color: $color-foreground;
  overflow-wrap: anywhere;
}

.profile-role {
  display: inline-block;
  margin: $space-md 0 0;
  padding: 3px $space-lg;
  font-size: $font-meta;
  font-weight: 500;
  line-height: 1.4;
  color: $color-primary;
  background: rgba(21, 128, 61, 0.08);
  border: 1px solid rgba(21, 128, 61, 0.16);
  border-radius: 999px;
  overflow-wrap: anywhere;
}

.profile-fields {
  margin: 0;
  padding: $space-md $space-2xl $space-xl;
}

.profile-field {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  column-gap: $space-lg;
  align-items: center;
  padding: $space-lg 0;
}

.profile-field + .profile-field {
  border-top: 1px solid $color-border;
}

.profile-field__icon {
  grid-row: 1 / 3;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: $radius-md;
  background: rgba(21, 128, 61, 0.08);
  color: $color-primary;
  font-size: 18px;
}

.profile-field dt {
  grid-column: 2;
  margin: 0;
  font-size: $font-meta;
  line-height: 1.4;
  color: $color-muted-foreground;
}

.profile-field dd {
  grid-column: 2;
  margin: $space-xs 0 0;
  min-inline-size: 0;
  font-size: $font-body;
  font-weight: 500;
  line-height: 1.45;
  color: $color-foreground;
  overflow-wrap: anywhere;
}

.password-card__header {
  display: flex;
  align-items: center;
  gap: $space-lg;
  margin: 0 0 $space-2xl;
  padding-bottom: $space-xl;
  border-bottom: 1px solid $color-border;
}

.password-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: $radius-md;
  background: rgba(21, 128, 61, 0.08);
  color: $color-primary;
  font-size: 20px;
}

.password-card__heading {
  min-width: 0;
}

.profile-card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  line-height: 1.3;
  color: $color-foreground;
}

.password-card__desc {
  margin: $space-xs 0 0;
  font-size: $font-meta;
  color: $color-muted-foreground;
}

.password-card__body {
  display: grid;
  grid-template-columns: minmax(0, 420px) minmax(0, 1fr);
  gap: $space-3xl;
  align-items: start;
}

.pwd-tips {
  margin: 0;
  padding: $space-xl;
  background: $color-background;
  border: 1px solid $color-border;
  border-radius: $radius-md;
}

.pwd-tips__title {
  margin: 0 0 $space-md;
  font-size: $font-num;
  font-weight: 700;
  line-height: 1.4;
  color: $color-foreground;
}

.pwd-tips__list {
  margin: 0;
  padding-left: 16px;
}

.pwd-tips__list li {
  font-size: $font-meta;
  line-height: 1.5;
  color: $color-muted-foreground;
}

.pwd-tips__list li + li {
  margin-top: $space-md;
}

@keyframes profile-rise {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 991px) {
  .profile-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 860px) {
  .password-card__body {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (prefers-reduced-motion: reduce) {
  .profile-card {
    animation: none;
  }
}
</style>
