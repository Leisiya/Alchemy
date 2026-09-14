package com.ruoyi.common.utils;

import com.ruoyi.common.constant.UserConstants;

/**
 * 登录标识（用户名或邮箱）长度规则。
 */
public final class LoginIdentityUtils
{
    private LoginIdentityUtils()
    {
    }

    public static boolean isLoginIdLengthValid(String username)
    {
        if (StringUtils.isEmpty(username))
        {
            return false;
        }
        int len = username.length();
        if (username.indexOf('@') > 0)
        {
            return len <= UserConstants.EMAIL_MAX_LENGTH;
        }
        return len >= UserConstants.USERNAME_MIN_LENGTH
                && len <= UserConstants.USERNAME_MAX_LENGTH;
    }
}
