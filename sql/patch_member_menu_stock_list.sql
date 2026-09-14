-- 会员侧栏：只保留顶部「股票列表」（前端 index），去掉系统管理与重复的股票菜单
-- 可重复执行

-- 按钮权限：列表（若无则补）
insert into sys_menu (
  menu_id, menu_name, parent_id, order_num, path, component, query, route_name,
  is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark
)
select 1063, '筛股列表', 118, 3, '#', '', '', '', 1, 0, 'F', '0', '0', 'stock:screener:list', '#', 'admin', sysdate(), ''
from dual
where not exists (select 1 from sys_menu where menu_id = 1063);

-- 会员角色：移除系统管理 / 股票目录 / 列表页菜单（避免侧栏重复）
delete from sys_role_menu where role_id in (2, 3) and menu_id in (1, 5, 118);

-- 会员角色：仅保留按钮权限（不出现在侧栏）
insert ignore into sys_role_menu values ('2', '1061');
insert ignore into sys_role_menu values ('2', '1062');
insert ignore into sys_role_menu values ('2', '1063');
insert ignore into sys_role_menu values ('3', '1061');
insert ignore into sys_role_menu values ('3', '1062');
insert ignore into sys_role_menu values ('3', '1063');

-- 管理端菜单文案统一（管理员仍可见）
update sys_menu set menu_name = '股票列表', remark = '股票列表目录' where menu_id = 5;
update sys_menu set menu_name = '股票列表', remark = '股票列表菜单' where menu_id = 118;
