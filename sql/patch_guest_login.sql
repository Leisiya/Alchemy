-- 共享访客账号（已有库可重复执行；不要重跑整份 ry_20260417.sql）
insert into sys_role (role_name, role_key, role_sort, data_scope, menu_check_strictly, dept_check_strictly, status, del_flag, create_by, create_time, remark)
select '访客', 'guest', 4, '1', 1, 1, '0', '0', 'admin', sysdate(), '共享访客，禁止密码登录'
from dual
where not exists (select 1 from sys_role where role_key = 'guest' and del_flag = '0');

insert into sys_user (user_name, nick_name, user_type, email, phonenumber, sex, avatar, password, status, del_flag, login_ip, login_date, pwd_update_date, create_by, create_time, remark)
select 'guest', '访客用户', '01', '', '', '2', '', '$2a$10$r6Xb4ccjgHoncOMcDJeUUe5Gz0MfWVuT8hjwHaGy1cTBIQH2j9Yj6', '0', '0', '127.0.0.1', sysdate(), sysdate(), 'admin', sysdate(), '共享访客账号，禁止密码登录'
from dual
where not exists (select 1 from sys_user where user_name = 'guest' and del_flag = '0');

-- 同名普通用户（user_name=guest 且非访客）不转换为访客，不绑定访客角色
insert ignore into sys_user_role (user_id, role_id)
select u.user_id, r.role_id
from sys_user u
join sys_role r on r.role_key = 'guest' and r.del_flag = '0'
where u.user_name = 'guest' and u.user_type = '01' and u.del_flag = '0';

insert ignore into sys_role_menu (role_id, menu_id)
select r.role_id, m.menu_id
from sys_role r
join (select 1061 as menu_id union select 1062 union select 1063) m
where r.role_key = 'guest' and r.del_flag = '0';

insert into sys_config (config_name, config_key, config_value, config_type, create_by, create_time, remark)
select '账号自助-是否开启访客体验', 'sys.account.guestLogin', 'true', 'Y', 'admin', sysdate(), '是否开启登录页访客体验（true开启，false关闭）'
from dual
where not exists (select 1 from sys_config where config_key = 'sys.account.guestLogin');
