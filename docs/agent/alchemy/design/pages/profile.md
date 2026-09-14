# Profile Overrides

> **PROJECT:** Alchemy
> Rules here **override** `docs/agent/alchemy/design/MASTER.md` for `/user/profile` only.

## Layout

- Desktop: two-column grid — `360px` identity card + flexible password card, `gap: 24px`, content `max-width: 1200px`. Stacks to a single column below `992px`.
- Page header: `h1` 个人中心 + one muted subtitle line.
- Cards: radius 12px (`$radius-lg`), `$shadow-card`, subtle 200ms fade-up entrance (60ms stagger), disabled under `prefers-reduced-motion`.

## Identity

- Letter avatar only (`UserLetterAvatar` size `lg` / 80px) with a 4px card-colored ring, overlapping a 96px green-gradient cover (primary `#166534 → #15803D → #1D9A51`, low-opacity white radial highlights only — no photos, no patterns with meaning).
- Name 18px/700 centered under the avatar; role shown as a green-tint pill chip (`rgba(21,128,61,0.08)` bg), not a second editable field.
- Field rows: 36px tinted icon square (RuoYi sprite: `people` / `user` / `email` / `date`, `aria-hidden`) + 12px muted label over 14px/500 value; hairline dividers between rows. Read-only data stays a `dl`, never disabled inputs.
- Show 用户名称, 用户邮箱, 创建日期. Show 昵称 only when it differs from 用户名称.
- No 手机号码. No 性别. No photo upload. No `profile.jpg`.

## Password

- Card header: 40px tinted icon square (`password` sprite) + 16px title + 12px muted description, hairline divider below.
- Form `max-width: 420px`, visible labels on top (13px/500), default-size inputs and buttons (no `mini`).
- Static hint under 新密码 mirrors the active `pwdChrType` rule (`aria-describedby` linked).
- `show-password`. `autocomplete` `current-password` / `new-password`. Paste allowed.
- Native submit so Enter works. Save stays primary. Close is a default button, not destructive red.
- Failed validation: inline field errors plus a focusable `role="alert"` summary at the top of the form (soft red panel, 3px left accent).

## Out of scope

- Admin user CRUD (`/system/user`) may still show phone and gender.
- Do not delete Java avatar/profile update endpoints.
