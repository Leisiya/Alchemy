# Login / Register / Forgot-password Overrides

> **PROJECT:** Alchemy
> Rules here **override** `docs/agent/alchemy/design/MASTER.md` for auth surfaces only.

---

## Color

- Background: `#0D1B2A` with a restrained radial highlight. Not OLED pure black as a full-app theme.
- Card: translucent glass (`rgba(255,255,255,0.06)` + 1px `rgba(255,255,255,0.08)` border, `backdrop-filter: blur(8px)`), radius 16px, width 420px.
- CTA fill: Master `--color-primary` `#15803D` (same as workbench). Hover `#166534`.
- Title: `#FFFFFF`. Subtitle / links / checkbox: at least `#94A3B8` on the navy ground (4.5:1).
- Placeholder: `#94A3B8`. Input text: `#FFFFFF`.
- Focus ring / input focus border: `--color-ring` `#15803D`.
- Login/Register segmented tab: inactive `#94A3B8` on translucent track; active fill `#15803D` with white label.

## Typography

- Keep CJK system stack from Master. Page title is `h1`.

## Layout

- Login and register share one card chrome: title, product subtitle, then a two-tab switch (`/login` ↔ `/register`). Do not use a small “立即注册” / “使用已有账户登录” link under the primary button.
- Forgot-password stays a separate route with subtitle “找回密码” and a “返回登录” link. No tab switch.
- Register field order: email → password → confirm password → email OTP (send on the right) → submit. Forgot-password: email → new password → confirm → email OTP → reset.
- Email OTP row left edge aligns with the fields above; only the right side yields space for the send button.
- No extra username field. No “返回首页”.
- Below the primary login button, a full-width `type="button"`「访客体验」secondary control (`auth-guest-btn`): translucent fill, `#94A3B8` label, hover/focus uses `#15803D`. Independent loading「进入中...」. Hidden when `guestEnabled` is false. Do not native-submit the login form.

## Interaction

- No visible `el-form-item` labels or required asterisks. Placeholder is the only on-canvas field name (`请输入邮箱` / `请输入密码` / `请输入验证码` / …). Keep `id` and a matching `aria-label`.
- Native `autocomplete`: login username `username`, register/forgot email `email`, passwords `current-password` or `new-password`. Email OTP uses `one-time-code`. Graphic captcha (when enabled) uses `autocomplete="off"` and placeholder “请输入图形验证码” so it does not steal the email OTP autofill.
- Allow paste. Prefix SVG icons `aria-hidden="true"`.
- `@submit.native.prevent` + submit button `native-type="submit"` so Enter works from the email field.
- Empty initial credentials. Do not prefill `admin` / `admin123`.
- Graphic captcha (`sys.account.captchaEnabled`, default off): refresh is a `button` with `aria-label="刷新验证码"`; image has `alt`.
- Email OTP is inline on the same form (input + `type="button"` send / countdown). Do not jump to a second step, toast “已发送”, and repeat it in the subtitle.
- Send email OTP only after email format, password strength, and confirm-password match pass. Do not validate the OTP field itself before send. Graphic captcha (when enabled) is still only consumed on submit.
- Failed validation: inline field errors only. Focus the first invalid field after failed submit. Do not show a top-of-form error summary on login / register / forgot-password.
- Tab switch uses `router-link` with `aria-current="page"` on the active tab. Hover/active color only; no layout-shifting translate.
- After successful register: do not show a blocking MessageBox. Apply the session token and route to `redirect` (same on-site rule as login) or `/`. Use `$modal.msgSuccess('注册成功')`. While navigating, the submit label is「正在进入...」, not「注册中...」. If auto-login fails after the account exists, toast「注册成功，请登录」and go to `/login` with the current query. Do not use red success copy or a Confirm button.

## Motion

- Button hover 150–200ms color change only. No layout-shifting translate.
