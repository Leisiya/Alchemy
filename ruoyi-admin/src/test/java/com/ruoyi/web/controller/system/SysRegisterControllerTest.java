package com.ruoyi.web.controller.system;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.ruoyi.common.constant.Constants;
import com.ruoyi.common.constant.HttpStatus;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.model.RegisterBody;
import com.ruoyi.framework.web.service.SysLoginService;
import com.ruoyi.framework.web.service.SysRegisterService;
import com.ruoyi.system.service.ISysConfigService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class SysRegisterControllerTest
{
    @Mock
    private SysRegisterService registerService;

    @Mock
    private ISysConfigService configService;

    @Mock
    private SysLoginService loginService;

    @InjectMocks
    private SysRegisterController controller;

    @Test
    void registerSuccessReturnsToken()
    {
        RegisterBody user = new RegisterBody();
        user.setEmail("a@b.com");
        user.setPassword("secret1");
        when(configService.selectConfigByKey("sys.account.registerUser")).thenReturn("true");
        when(registerService.register(user)).thenReturn("");
        when(loginService.loginAfterVerified("a@b.com", "secret1")).thenReturn("tok-1");

        AjaxResult result = controller.register(user);

        assertEquals(HttpStatus.SUCCESS, result.get(AjaxResult.CODE_TAG));
        assertEquals("tok-1", result.get(Constants.TOKEN));
        verify(loginService).loginAfterVerified("a@b.com", "secret1");
    }

    @Test
    void registerSuccessOmitsTokenWhenAutoLoginFails()
    {
        RegisterBody user = new RegisterBody();
        user.setEmail("a@b.com");
        user.setPassword("secret1");
        when(configService.selectConfigByKey("sys.account.registerUser")).thenReturn("true");
        when(registerService.register(user)).thenReturn("");
        when(loginService.loginAfterVerified("a@b.com", "secret1"))
                .thenThrow(new RuntimeException("auto-login failed"));

        AjaxResult result = controller.register(user);

        assertEquals(HttpStatus.SUCCESS, result.get(AjaxResult.CODE_TAG));
        assertNull(result.get(Constants.TOKEN));
    }

    @Test
    void registerErrorDoesNotIssueToken()
    {
        RegisterBody user = new RegisterBody();
        user.setEmail("a@b.com");
        user.setPassword("secret1");
        when(configService.selectConfigByKey("sys.account.registerUser")).thenReturn("true");
        when(registerService.register(user)).thenReturn("该邮箱已被注册");

        AjaxResult result = controller.register(user);

        assertEquals(HttpStatus.ERROR, result.get(AjaxResult.CODE_TAG));
        assertNull(result.get(Constants.TOKEN));
        verify(loginService, never()).loginAfterVerified("a@b.com", "secret1");
    }
}
