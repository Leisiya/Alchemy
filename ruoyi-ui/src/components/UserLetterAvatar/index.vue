<template>
  <span
    class="user-letter-avatar"
    :class="'is-' + size"
    aria-hidden="true"
  >{{ initial }}</span>
</template>

<script>
import { mapGetters } from 'vuex'
import { userLetterInitial } from '@/utils/userLetterInitial'

export default {
  name: 'UserLetterAvatar',
  props: {
    size: {
      type: String,
      default: 'sm',
      validator(value) {
        return ['sm', 'md', 'lg'].indexOf(value) !== -1
      }
    }
  },
  computed: {
    ...mapGetters(['nickName', 'name']),
    initial() {
      return userLetterInitial(this.nickName, this.name)
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/assets/styles/tokens.scss";

.user-letter-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 50%;
  background: $color-primary;
  color: $color-on-primary;
  font-weight: 700;
  line-height: 1;
  transition: background $motion-base ease;
}

.user-letter-avatar.is-sm {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.user-letter-avatar.is-md {
  width: 48px;
  height: 48px;
  font-size: 18px;
}

.user-letter-avatar.is-lg {
  width: 80px;
  height: 80px;
  font-size: 32px;
}

@media (prefers-reduced-motion: reduce) {
  .user-letter-avatar {
    transition: none;
  }
}
</style>
