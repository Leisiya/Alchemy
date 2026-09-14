package com.ruoyi.web.controller.system;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import java.util.Collections;
import com.ruoyi.common.constant.Constants;
import com.ruoyi.common.constant.HttpStatus;
import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.entity.SysRole;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.framework.web.service.SysLoginService;
import com.ruoyi.framework.web.service.SysPermissionService;
import com.ruoyi.framework.web.service.TokenService;
import com.ruoyi.system.service.ISysConfigService;
import com.ruoyi.system.service.ISysMenuService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;

@ExtendWith(MockitoExtension.class)
class SysLoginControllerTest
{
    @Mock
    private SysLoginService loginService;
    @Mock
    private ISysMenuService menuService;
    @Mock
    private SysPermissionService permissionService;
    @Mock
    private TokenService tokenService;
    @Mock
    private ISysConfigService configService;

    @InjectMocks
    private SysLoginController controller;

    @AfterEach
    void clearSecurityContext()
    {
        SecurityContextHolder.clearContext();
    }

    private SysUser user(Long id, String type, String roleKey)
    {
        SysUser user = new SysUser(id);
        user.setUserType(type);
        if (roleKey != null)
        {
            SysRole role = new SysRole();
            role.setRoleKey(roleKey);
            user.setRoles(Collections.singletonList(role));
        }
        return user;
    }

    @Test
    void guestLoginReturnsToken()
    {
        when(loginService.guestLogin()).thenReturn("guest-tok");
        AjaxResult result = controller.guestLogin();
        assertEquals(HttpStatus.SUCCESS, result.get(AjaxResult.CODE_TAG));
        assertEquals("guest-tok", result.get(Constants.TOKEN));
    }

    @Test
    void getInfoMarksGuestAndSkipsPasswordPrompts()
    {
        LoginUser loginUser = new LoginUser(3L, null,
                user(3L, UserConstants.USER_TYPE_GUEST, UserConstants.GUEST_ROLE_KEY), Collections.emptySet());
        UsernamePasswordAuthenticationToken auth =
                new UsernamePasswordAuthenticationToken(loginUser, null, Collections.emptyList());
        SecurityContextHolder.getContext().setAuthentication(auth);
        when(permissionService.getRolePermission(any())).thenReturn(Collections.emptySet());
        when(permissionService.getMenuPermission(any())).thenReturn(Collections.emptySet());

        AjaxResult result = controller.getInfo();

        assertEquals(Boolean.TRUE, result.get("isGuest"));
        assertEquals(Boolean.FALSE, result.get("isDefaultModifyPwd"));
        assertEquals(Boolean.FALSE, result.get("isPasswordExpired"));
    }
}
