package com.ruoyi.web.controller.system;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.model.ResetPwdByEmailBody;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.framework.web.service.SysForgetPasswordService;

/**
 * 找回密码（邮箱验证码重置密码）
 * 
 * @author ruoyi
 */
@RestController
public class SysForgetPasswordController extends BaseController
{
    @Autowired
    private SysForgetPasswordService forgetPasswordService;

    /**
     * 发送找回密码邮箱验证码
     */
    @PostMapping("/resetPwd/emailCode")
    public AjaxResult sendEmailCode(@RequestParam String email)
    {
        String msg = forgetPasswordService.sendEmailCode(email);
        return StringUtils.isEmpty(msg) ? success() : error(msg);
    }

    /**
     * 通过邮箱验证码重置密码
     */
    @PostMapping("/resetPwd/byEmail")
    public AjaxResult resetPwdByEmail(@RequestBody ResetPwdByEmailBody body)
    {
        String msg = forgetPasswordService.resetPassword(body);
        return StringUtils.isEmpty(msg) ? success() : error(msg);
    }
}
