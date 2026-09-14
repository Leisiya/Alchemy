<template>
  <el-form
    ref="form"
    class="pwd-form"
    :model="user"
    :rules="formRules"
    label-position="top"
    @submit.native.prevent="submit"
  >
    <div
      v-if="submitErrors.length"
      ref="errorSummary"
      class="pwd-error-summary"
      role="alert"
      tabindex="-1"
      aria-labelledby="pwd-error-title"
    >
      <p id="pwd-error-title" class="pwd-error-title">请修正以下问题</p>
      <ul>
        <li v-for="(item, index) in submitErrors" :key="index">
          <a :href="'#' + item.id" @click.prevent="focusField(item.id)">{{ item.message }}</a>
        </li>
      </ul>
    </div>
    <el-form-item label="旧密码" prop="oldPassword">
      <el-input
        id="oldPassword"
        v-model="user.oldPassword"
        placeholder="请输入旧密码"
        type="password"
        show-password
        autocomplete="current-password"
      />
    </el-form-item>
    <el-form-item label="新密码" prop="newPassword" :rules="infoPwdValidator">
      <el-input
        id="newPassword"
        v-model="user.newPassword"
        placeholder="请输入新密码"
        type="password"
        show-password
        autocomplete="new-password"
        aria-describedby="pwdHint"
      />
      <p id="pwdHint" class="pwd-hint">{{ pwdHint }}</p>
    </el-form-item>
    <el-form-item label="确认密码" prop="confirmPassword">
      <el-input
        id="confirmPassword"
        v-model="user.confirmPassword"
        placeholder="请确认新密码"
        type="password"
        show-password
        autocomplete="new-password"
      />
    </el-form-item>
    <el-form-item class="pwd-actions">
      <el-button type="primary" native-type="submit">保存</el-button>
      <el-button native-type="button" @click="close">关闭</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import { updateUserPwd } from '@/api/system/user'
import passwordRule from '@/utils/passwordRule'

export default {
  mixins: [passwordRule],
  data() {
    return {
      submitErrors: [],
      user: {
        oldPassword: undefined,
        newPassword: undefined,
        confirmPassword: undefined
      }
    }
  },
  computed: {
    pwdHint() {
      switch (this.pwdChrType) {
        case '1':
          return '6-20 位数字'
        case '2':
          return '6-20 位英文字母'
        case '3':
          return '6-20 位，需同时包含字母和数字'
        case '4':
          return '6-20 位，需同时包含字母、数字和特殊字符'
        default:
          return '长度为 6-20 个字符'
      }
    },
    formRules() {
      return {
        oldPassword: [
          { required: true, message: '旧密码不能为空', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '确认密码不能为空', trigger: 'blur' },
          {
            validator: (rule, value, callback) => {
              if (this.user.newPassword !== value) {
                callback(new Error('两次输入的密码不一致'))
              } else {
                callback()
              }
            },
            trigger: 'blur'
          }
        ]
      }
    }
  },
  methods: {
    focusField(id) {
      const el = document.getElementById(id)
      if (el && el.focus) {
        el.focus()
      }
    },
    submit() {
      this.submitErrors = []
      this.$refs.form.validate((valid, fields) => {
        if (!valid) {
          const messages = []
          Object.keys(fields || {}).forEach(key => {
            (fields[key] || []).forEach(err => {
              messages.push({ id: key, message: err.message })
            })
          })
          this.submitErrors = messages
          this.$nextTick(() => {
            const node = this.$refs.errorSummary
            if (node && node.focus) {
              node.focus()
            }
          })
          return
        }
        updateUserPwd(this.user.oldPassword, this.user.newPassword).then(() => {
          this.$modal.msgSuccess('修改成功')
        })
      })
    },
    close() {
      this.$tab.closePage()
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/assets/styles/tokens.scss";

.pwd-form {
  max-width: 420px;
}

.pwd-form ::v-deep .el-form-item {
  margin-bottom: $space-2xl;
}

.pwd-form ::v-deep .el-form-item__label {
  padding: 0 0 $space-md;
  font-size: $font-num;
  font-weight: 500;
  line-height: 1.4;
  color: $color-foreground;
}

.pwd-form ::v-deep .el-form-item.is-error .el-input__inner,
.pwd-form ::v-deep .el-form-item.is-error .el-input__inner:focus {
  border-color: $color-destructive;
}

.pwd-hint {
  margin: $space-md 0 0;
  font-size: $font-meta;
  line-height: 1.4;
  color: $color-muted-foreground;
}

.pwd-actions {
  margin-bottom: 0;
}

.pwd-error-summary {
  margin: 0 0 $space-2xl;
  padding: $space-lg $space-xl;
  border: 1px solid rgba(220, 38, 38, 0.24);
  border-left: 3px solid $color-destructive;
  border-radius: $radius-md;
  background: #FEF2F2;
}

.pwd-error-title {
  margin: 0 0 $space-sm;
  font-size: $font-num;
  font-weight: 700;
  color: $color-destructive;
}

.pwd-error-summary ul {
  margin: 0;
  padding-left: 18px;
}

.pwd-error-summary li + li {
  margin-top: $space-xs;
}

.pwd-error-summary a {
  color: $color-destructive;
}
</style>
