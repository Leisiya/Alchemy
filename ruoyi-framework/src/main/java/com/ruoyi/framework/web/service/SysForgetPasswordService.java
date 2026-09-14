package com.ruoyi.framework.web.service;

import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import com.ruoyi.common.constant.CacheConstants;
import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.ResetPwdByEmailBody;
import com.ruoyi.common.core.redis.RedisCache;
import com.ruoyi.common.utils.MailUtils;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.system.service.ISysUserService;

/**
 * 找回密码（邮箱验证码重置密码）校验方法
 * 
 * @author ruoyi
 */
@Component
public class SysForgetPasswordService
{
    private static final Pattern EMAIL_PATTERN = Pattern.compile("^[\\w.-]+@[\\w-]+(\\.[\\w-]+)+$");

    /** 邮箱验证码有效期（分钟） */
    private static final long EMAIL_CODE_EXPIRE_MINUTES = 10;

    /** 邮箱验证码重发冷却时间（秒） */
    private static final long EMAIL_CODE_LIMIT_SECONDS = 60;

    @Autowired
    private ISysUserService userService;

    @Autowired
    private RedisCache redisCache;

    /**
     * 发送找回密码邮箱验证码
     *
     * @param email 邮箱
     * @return 错误信息，成功返回空字符串
     */
    public String sendEmailCode(String email)
    {
        if (StringUtils.isEmpty(email) || !EMAIL_PATTERN.matcher(email).matches())
        {
            return "邮箱格式不正确";
        }
        SysUser user = userService.selectUserByEmail(email);
        if (StringUtils.isNull(user))
        {
            return "该邮箱尚未注册";
        }
        String limitKey = CacheConstants.RESET_PWD_EMAIL_CODE_LIMIT_KEY + email;
        if (redisCache.hasKey(limitKey))
        {
            return "验证码发送过于频繁，请稍后再试";
        }

        String code = generateCode();
        redisCache.setCacheObject(CacheConstants.RESET_PWD_EMAIL_CODE_KEY + email, code, (int) EMAIL_CODE_EXPIRE_MINUTES, TimeUnit.MINUTES);
        redisCache.setCacheObject(limitKey, code, (int) EMAIL_CODE_LIMIT_SECONDS, TimeUnit.SECONDS);
        MailUtils.sendVerificationCode(email, "【Alchemy】重置密码验证码", code);
        return "";
    }

    /**
     * 通过邮箱验证码重置密码
     *
     * @param body 请求参数
     * @return 错误信息，成功返回空字符串
     */
    public String resetPassword(ResetPwdByEmailBody body)
    {
        String email = body.getEmail(), newPassword = body.getNewPassword();
        if (StringUtils.isEmpty(email) || !EMAIL_PATTERN.matcher(email).matches())
        {
            return "邮箱格式不正确";
        }
        if (StringUtils.isEmpty(newPassword) || StringUtils.isEmpty(body.getConfirmPassword()))
        {
            return "新密码不能为空";
        }
        if (!newPassword.equals(body.getConfirmPassword()))
        {
            return "两次输入的密码不一致";
        }
        if (newPassword.length() < UserConstants.PASSWORD_MIN_LENGTH
                || newPassword.length() > UserConstants.PASSWORD_MAX_LENGTH)
        {
            return "密码长度必须在5到20个字符之间";
        }

        SysUser user = userService.selectUserByEmail(email);
        if (StringUtils.isNull(user))
        {
            return "该邮箱尚未注册";
        }

        String codeKey = CacheConstants.RESET_PWD_EMAIL_CODE_KEY + email;
        String cacheCode = redisCache.getCacheObject(codeKey);
        if (StringUtils.isEmpty(cacheCode))
        {
            return "邮箱验证码已过期，请重新获取";
        }
        if (!cacheCode.equals(body.getEmailCode()))
        {
            return "邮箱验证码不正确";
        }

        userService.resetUserPwd(user.getUserId(), SecurityUtils.encryptPassword(newPassword));
        redisCache.deleteObject(codeKey);
        return "";
    }

    /**
     * 生成6位数字验证码
     */
    private String generateCode()
    {
        return String.valueOf(ThreadLocalRandom.current().nextInt(100000, 1000000));
    }
}
