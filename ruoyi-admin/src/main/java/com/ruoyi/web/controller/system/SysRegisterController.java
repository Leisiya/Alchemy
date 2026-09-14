package com.ruoyi.web.controller.system;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.constant.Constants;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.model.RegisterBody;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.framework.web.service.SysLoginService;
import com.ruoyi.framework.web.service.SysRegisterService;
import com.ruoyi.system.service.ISysConfigService;

/**
 * 注册验证
 *
 * @author ruoyi
 */
@RestController
public class SysRegisterController extends BaseController
{
    @Autowired
    private SysRegisterService registerService;

    @Autowired
    private ISysConfigService configService;

    @Autowired
    private SysLoginService loginService;

    @PostMapping("/register")
    public AjaxResult register(@RequestBody RegisterBody user)
    {
        if (!("true".equals(configService.selectConfigByKey("sys.account.registerUser"))))
        {
            return error("当前系统没有开启注册功能！");
        }
        String msg = registerService.register(user);
        if (StringUtils.isNotEmpty(msg))
        {
            return error(msg);
        }
        AjaxResult ajax = success("注册成功");
        try
        {
            String token = loginService.loginAfterVerified(user.getEmail(), user.getPassword());
            ajax.put(Constants.TOKEN, token);
        }
        catch (Exception e)
        {
            logger.warn("注册成功但自动登录失败", e);
        }
        return ajax;
    }

    /**
     * 发送注册邮箱验证码
     */
    @PostMapping("/register/emailCode")
    public AjaxResult sendEmailCode(@RequestParam String email)
    {
        if (!("true".equals(configService.selectConfigByKey("sys.account.registerUser"))))
        {
            return error("当前系统没有开启注册功能！");
        }
        String msg = registerService.sendEmailCode(email);
        return StringUtils.isEmpty(msg) ? success() : error(msg);
    }
}
