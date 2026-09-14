package com.ruoyi.framework.web.service;

import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import com.ruoyi.common.constant.CacheConstants;
import com.ruoyi.common.constant.Constants;
import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.RegisterBody;
import com.ruoyi.common.core.redis.RedisCache;
import com.ruoyi.common.exception.user.CaptchaException;
import com.ruoyi.common.exception.user.CaptchaExpireException;
import com.ruoyi.common.utils.DateUtils;
import com.ruoyi.common.utils.MailUtils;
import com.ruoyi.common.utils.MessageUtils;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.framework.manager.AsyncManager;
import com.ruoyi.framework.manager.factory.AsyncFactory;
import com.ruoyi.system.service.ISysConfigService;
import com.ruoyi.system.service.ISysUserService;

/**
 * 注册校验方法
 * 
 * @author ruoyi
 */
@Component
public class SysRegisterService
{
    private static final Pattern EMAIL_PATTERN = Pattern.compile("^[\\w.-]+@[\\w-]+(\\.[\\w-]+)+$");

    /** 邮箱验证码有效期（分钟） */
    private static final long EMAIL_CODE_EXPIRE_MINUTES = 10;

    /** 邮箱验证码重发冷却时间（秒） */
    private static final long EMAIL_CODE_LIMIT_SECONDS = 60;

    /** 邮箱本地部分最大截取长度，为随机后缀预留空间（user_name 列宽 30） */
    private static final int EMAIL_PREFIX_MAX_LENGTH = 26;

    /** 用户名前缀冲突时最大重试次数 */
    private static final int USERNAME_RETRY_TIMES = 5;

    @Autowired
    private ISysUserService userService;

    @Autowired
    private ISysConfigService configService;

    @Autowired
    private RedisCache redisCache;

    /**
     * 发送注册邮箱验证码
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
        SysUser checkUser = new SysUser();
        checkUser.setEmail(email);
        if (!userService.checkEmailUnique(checkUser))
        {
            return "该邮箱已被注册";
        }
        String limitKey = CacheConstants.EMAIL_CODE_LIMIT_KEY + email;
        if (redisCache.hasKey(limitKey))
        {
            return "验证码发送过于频繁，请稍后再试";
        }

        String code = generateCode();
        redisCache.setCacheObject(CacheConstants.EMAIL_CODE_KEY + email, code, (int) EMAIL_CODE_EXPIRE_MINUTES, TimeUnit.MINUTES);
        redisCache.setCacheObject(limitKey, code, (int) EMAIL_CODE_LIMIT_SECONDS, TimeUnit.SECONDS);
        MailUtils.sendVerificationCode(email, "【Alchemy】注册验证码", code);
        return "";
    }

    /**
     * 注册
     */
    public String register(RegisterBody registerBody)
    {
        String email = registerBody.getEmail(), password = registerBody.getPassword();

        // 验证码开关（图形验证码）
        boolean captchaEnabled = configService.selectCaptchaEnabled();
        if (captchaEnabled)
        {
            validateCaptcha(email, registerBody.getCode(), registerBody.getUuid());
        }

        if (StringUtils.isEmpty(email) || !EMAIL_PATTERN.matcher(email).matches())
        {
            return "邮箱格式不正确";
        }
        if (StringUtils.isEmpty(password))
        {
            return "用户密码不能为空";
        }
        if (password.length() < UserConstants.PASSWORD_MIN_LENGTH
                || password.length() > UserConstants.PASSWORD_MAX_LENGTH)
        {
            return "密码长度必须在5到20个字符之间";
        }

        SysUser checkUser = new SysUser();
        checkUser.setEmail(email);
        if (!userService.checkEmailUnique(checkUser))
        {
            return "该邮箱已被注册";
        }

        String emailCodeKey = CacheConstants.EMAIL_CODE_KEY + email;
        String cacheCode = redisCache.getCacheObject(emailCodeKey);
        if (StringUtils.isEmpty(cacheCode))
        {
            return "邮箱验证码已过期，请重新获取";
        }
        if (!cacheCode.equals(registerBody.getEmailCode()))
        {
            return "邮箱验证码不正确";
        }

        String username = generateUniqueUsername(email);
        if (StringUtils.isEmpty(username))
        {
            return "注册失败，请稍后重试";
        }

        SysUser sysUser = new SysUser();
        sysUser.setUserName(username);
        sysUser.setNickName(username);
        sysUser.setEmail(email);
        sysUser.setPwdUpdateDate(DateUtils.getNowDate());
        sysUser.setPassword(SecurityUtils.encryptPassword(password));
        boolean regFlag = userService.registerUser(sysUser);
        if (!regFlag)
        {
            return "注册失败,请联系系统管理人员";
        }

        AsyncManager.me().execute(AsyncFactory.recordLogininfor(username, Constants.REGISTER, MessageUtils.message("user.register.success")));
        redisCache.deleteObject(emailCodeKey);
        return "";
    }

    /**
     * 根据邮箱前缀生成全局唯一的登录用户名，前缀冲突时自动追加随机数字尾巴
     *
     * @param email 邮箱
     * @return 唯一用户名，多次重试仍冲突时返回空字符串
     */
    private String generateUniqueUsername(String email)
    {
        String prefix = email.substring(0, email.indexOf('@'));
        if (prefix.length() > EMAIL_PREFIX_MAX_LENGTH)
        {
            prefix = prefix.substring(0, EMAIL_PREFIX_MAX_LENGTH);
        }

        SysUser checkUser = new SysUser();
        checkUser.setUserName(prefix);
        if (userService.checkUserNameUnique(checkUser))
        {
            return prefix;
        }

        for (int i = 0; i < USERNAME_RETRY_TIMES; i++)
        {
            String candidate = prefix + ThreadLocalRandom.current().nextInt(1000, 10000);
            checkUser.setUserName(candidate);
            if (userService.checkUserNameUnique(checkUser))
            {
                return candidate;
            }
        }
        return null;
    }

    /**
     * 生成6位数字验证码
     */
    private String generateCode()
    {
        return String.valueOf(ThreadLocalRandom.current().nextInt(100000, 1000000));
    }

    /**
     * 校验验证码
     * 
     * @param username 用户名
     * @param code 验证码
     * @param uuid 唯一标识
     * @return 结果
     */
    public void validateCaptcha(String username, String code, String uuid)
    {
        String verifyKey = CacheConstants.CAPTCHA_CODE_KEY + StringUtils.nvl(uuid, "");
        String captcha = redisCache.getCacheObject(verifyKey);
        redisCache.deleteObject(verifyKey);
        if (captcha == null)
        {
            throw new CaptchaExpireException();
        }
        if (!code.equalsIgnoreCase(captcha))
        {
            throw new CaptchaException();
        }
    }
}
