# Splash / First-paint Overrides

> **PROJECT:** Alchemy
> Rules here **override** `docs/agent/alchemy/design/MASTER.md` for the HTML first-paint loader in `ruoyi-ui/public/index.html` only.

---

## Surface

- This screen is auth-adjacent: same navy ground as login (`#0D1B2A`) and the same restrained radial highlight (`circle at 50% 0%`, `#1b3a5f` → `#0D1B2A`).
- Navy belongs **only** on `.app-splash` (`position: fixed; inset: 0`). Do not set `background` on `html`, `body`, or `#app` — those rules stay after Vue mounts and would tint the light workbench.
- Do not reuse the RuoYi purple curtain (`#7171C6` / `#7171C6`) or nested white spin rings.
- Primary green `#15803D` is the spinner accent only. Do not fill the viewport with it.

## Content

- Brand wordmark `Alchemy` (28px / 700 / white), then login subtitle `A股价值投资好助手` (`#94A3B8`, 14px).
- Status copy is short: `正在加载`. Do not use “正在加载系统资源，请耐心等待”.
- Inline CSS only. Vue replaces `#app` when the bundle mounts; do not add JS fade/curtain classes.

## Motion & a11y

- One 32px spinner. CSS only, ~800ms linear rotate. Track is muted slate; the moving half-arc is `#15803D`.
- `role="status"`, `aria-live="polite"`, `aria-busy="true"`. Decorative spinner `aria-hidden="true"`.
- `@media (prefers-reduced-motion: reduce)`: stop rotation; keep a static ring.
- CJK system stack from Master. No Open Sans / extra font files.
