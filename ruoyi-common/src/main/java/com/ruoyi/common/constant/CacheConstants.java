package com.ruoyi.common.constant;

/**
 * 缓存的key 常量
 * 
 * @author ruoyi
 */
public class CacheConstants
{
    /**
     * 登录用户 redis key
     */
    public static final String LOGIN_TOKEN_KEY = "login_tokens:";

    /**
     * 验证码 redis key
     */
    public static final String CAPTCHA_CODE_KEY = "captcha_codes:";

    /**
     * 参数管理 cache key
     */
    public static final String SYS_CONFIG_KEY = "sys_config:";

    /**
     * 字典管理 cache key
     */
    public static final String SYS_DICT_KEY = "sys_dict:";

    /**
     * 防重提交 redis key
     */
    public static final String REPEAT_SUBMIT_KEY = "repeat_submit:";

    /**
     * 限流 redis key
     */
    public static final String RATE_LIMIT_KEY = "rate_limit:";

    /**
     * 登录账户密码错误次数 redis key
     */
    public static final String PWD_ERR_CNT_KEY = "pwd_err_cnt:";

    /**
     * 注册邮箱验证码 redis key
     */
    public static final String EMAIL_CODE_KEY = "email_code:";

    /**
     * 注册邮箱验证码 发送冷却 redis key
     */
    public static final String EMAIL_CODE_LIMIT_KEY = "email_code_limit:";

    /**
     * 找回密码邮箱验证码 redis key
     */
    public static final String RESET_PWD_EMAIL_CODE_KEY = "reset_pwd_email_code:";

    /**
     * 找回密码邮箱验证码 发送冷却 redis key
     */
    public static final String RESET_PWD_EMAIL_CODE_LIMIT_KEY = "reset_pwd_email_code_limit:";
}
