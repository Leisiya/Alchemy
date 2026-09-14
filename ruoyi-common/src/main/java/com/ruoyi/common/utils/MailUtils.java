package com.ruoyi.common.utils;

import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.JavaMailSenderImpl;

import com.ruoyi.common.config.RuoYiConfig;
import com.ruoyi.common.utils.spring.SpringUtils;

/**
 * 邮件发送工具类
 *
 * @author ruoyi
 */
public class MailUtils
{
    public static String formatFromHeader(String address, String personal)
    {
        return personal + " <" + address + ">";
    }

    public static String resolveFromAddress(String configuredFrom, String smtpUsername)
    {
        return StringUtils.isNotEmpty(StringUtils.trim(configuredFrom)) ? configuredFrom.trim() : smtpUsername;
    }

    /**
     * 发送验证码邮件
     *
     * @param to 收件邮箱
     * @param subject 邮件主题
     * @param code 验证码
     */
    public static void sendVerificationCode(String to, String subject, String code)
    {
        JavaMailSender mailSender = SpringUtils.getBean(JavaMailSender.class);
        SimpleMailMessage message = new SimpleMailMessage();
        String from = ((JavaMailSenderImpl) mailSender).getUsername();
        String configuredFrom = SpringUtils.getBean(org.springframework.core.env.Environment.class).getProperty("spring.mail.from");
        String personal = SpringUtils.getBean(RuoYiConfig.class).getName();
        message.setFrom(formatFromHeader(resolveFromAddress(configuredFrom, from), personal));
        message.setTo(to);
        message.setSubject(subject);
        message.setText("您的验证码是：" + code + "，有效期10分钟，请勿泄露给他人。如非本人操作，请忽略此邮件。");
        mailSender.send(message);
    }
}
