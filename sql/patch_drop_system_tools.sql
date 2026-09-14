-- 去掉系统工具菜单与嵌套股票列表目录。筛股 F 按钮权限保留并挂到根节点。
-- 可重复执行。不要重跑完整 ry_20260417.sql。

delete from sys_role_menu where menu_id in (3, 115, 117, 5, 118);
update sys_menu set parent_id = 0 where menu_id in (1061, 1062, 1063);
delete from sys_menu where menu_id in (3, 115, 117, 5, 118);
