package com.ruoyi.framework.web.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.redis.RedisCache;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.common.utils.MessageUtils;
import com.ruoyi.common.utils.spring.SpringUtils;
import com.ruoyi.system.service.ISysConfigService;
import com.ruoyi.system.service.ISysUserService;
import jakarta.servlet.http.HttpServletRequest;
import java.util.Locale;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.beans.factory.support.DefaultListableBeanFactory;
import org.springframework.context.support.StaticMessageSource;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

@ExtendWith(MockitoExtension.class)
class SysLoginServiceGuestTest
{
    @Mock
    private TokenService tokenService;
    @Mock
    private AuthenticationManager authenticationManager;
    @Mock
    private RedisCache redisCache;
    @Mock
    private ISysUserService userService;
    @Mock
    private ISysConfigService configService;
    @Mock
    private UserDetailsServiceImpl userDetailsService;

    @InjectMocks
    private SysLoginService loginService;

    @AfterEach
    void clearRequestContext()
    {
        RequestContextHolder.resetRequestAttributes();
        new SpringUtils().postProcessBeanFactory(null);
    }

    private void bindRequestContext()
    {
        ServletRequestAttributes attributes = mock(ServletRequestAttributes.class);
        when(attributes.getRequest()).thenReturn(mock(HttpServletRequest.class));
        RequestContextHolder.setRequestAttributes(attributes);
    }

    private void bindUserNotExistsMessage()
    {
        StaticMessageSource messageSource = new StaticMessageSource();
        messageSource.addMessage("user.not.exists", Locale.getDefault(), "用户不存在/密码错误");
        DefaultListableBeanFactory factory = new DefaultListableBeanFactory();
        factory.registerSingleton("messageSource", messageSource);
        new SpringUtils().postProcessBeanFactory(factory);
    }

    @Test
    void guestLoginDisabled()
    {
        when(configService.selectConfigByKey("sys.account.guestLogin")).thenReturn("false");
        ServiceException ex = assertThrows(ServiceException.class, () -> loginService.guestLogin());
        assertEquals("访客体验未开启", ex.getMessage());
        verify(tokenService, never()).createToken(any());
    }

    @Test
    void loginAfterVerifiedRejectsGuest()
    {
        bindRequestContext();
        when(configService.selectConfigByKey("sys.login.blackIPList")).thenReturn("");
        SysUser guest = new SysUser(3L);
        guest.setUserType(UserConstants.USER_TYPE_GUEST);
        when(userService.selectUserByUserName("guest")).thenReturn(guest);
        ServiceException ex = assertThrows(ServiceException.class,
                () -> loginService.loginAfterVerified("guest", "123456"));
        assertEquals("请使用访客体验入口", ex.getMessage());
        verify(authenticationManager, never()).authenticate(any());
        verify(tokenService, never()).createToken(any());
    }

    @Test
    void guestLoginRejectsNonGuestNamedGuest()
    {
        bindRequestContext();
        bindUserNotExistsMessage();
        when(configService.selectConfigByKey("sys.account.guestLogin")).thenReturn("true");
        when(configService.selectConfigByKey("sys.login.blackIPList")).thenReturn("");
        SysUser namedGuest = new SysUser(10L);
        namedGuest.setUserName("guest");
        namedGuest.setUserType(UserConstants.USER_TYPE_SYS);
        when(userService.selectUserByUserName("guest")).thenReturn(namedGuest);

        ServiceException ex = assertThrows(ServiceException.class, () -> loginService.guestLogin());
        try
        {
            assertEquals(MessageUtils.message("user.not.exists"), ex.getMessage());
        }
        catch (Exception ignored)
        {
            assertFalse(ex.getMessage() == null || ex.getMessage().isBlank());
        }
        verify(tokenService, never()).createToken(any());
        verify(userDetailsService, never()).createLoginUser(any());
    }
}
