-- 去掉代码生成菜单与空表。Alchemy 已移除 ruoyi-generator（改由 AI/手工写 CRUD）。
-- 可重复执行。不要重跑完整 ry_20260417.sql。

delete from sys_role_menu where menu_id in (116, 1055, 1056, 1057, 1058, 1059, 1060);
delete from sys_menu where menu_id in (116, 1055, 1056, 1057, 1058, 1059, 1060);

update sys_menu set order_num = 2 where menu_id = 117 and path = 'swagger';

drop table if exists gen_table_column;
drop table if exists gen_table;
