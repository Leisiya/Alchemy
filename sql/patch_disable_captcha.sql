-- 关闭登录/注册图形验证码（邮箱验证码不受影响）
-- 可重复执行
-- 执行后请在「系统管理 → 参数设置」刷新缓存，或重启后端

UPDATE sys_config
SET config_value = 'false'
WHERE config_key = 'sys.account.captchaEnabled';
