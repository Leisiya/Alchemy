# Notice Center Overrides

> **PROJECT:** Alchemy
> Rules here **override** `docs/agent/alchemy/design/MASTER.md` for the notification inbox drawer (`NoticeDrawer`).

## Drawer chrome

- Title「通知中心」; RTL drawer; wrapper click closes.
- Desktop: **400px** wide.
- Mobile (`device === mobile`，小于 992px): drawer `size` **100%**.
- List view toolbar: left muted「暂无未读」or「{n} 条未读」; right text button「全部已读」（disabled when zero unread).
- Loading:「加载中…」; fetch error:「加载失败」; empty list:「暂无通知」.

## List row

Each row is a full-width `<button>` (not a table row):

| Zone | Content |
| --- | --- |
| Leading | 8px circle: primary green dot when unread; equal spacer when read (`aria-hidden`) |
| Top line | Left: type pill text — `1` →「通知」，`2` →「公告」; right: relative time（刚刚 / N分钟前 / N小时前 / 昨天 / `YYYY-MM-DD`） |
| Title | 14px/600, single-line ellipsis |
| Preview | 12px muted; strip HTML from `noticeContent`, collapse whitespace, max **80** chars +「…」, **2-line** clamp |

Row hover: muted background; `:focus-visible` ring per Master.

## Detail view

-「返回」text button restores the list (clears `activeId`).
- `h2` notice title; 12px muted absolute `createTime` (`parseTime`).
- Body: `v-html` on `noticeContent` (admin-authored HTML only).
- Opening a row marks it read (guest → `localStorage`; logged-in → `PUT /system/notice/read/{id}`).

## Out of scope

- Admin CRUD at `/system/notice` (RuoYi table page) — standard Element primary, not product chrome overrides.
- No top-of-page announcement strip; drawer is the only consumer-facing surface.
