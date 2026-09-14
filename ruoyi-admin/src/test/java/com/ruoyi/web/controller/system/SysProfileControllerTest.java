package com.ruoyi.web.controller.system;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.domain.entity.SysRole;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.framework.web.service.TokenService;
import com.ruoyi.system.service.ISysUserService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;

@ExtendWith(MockitoExtension.class)
class SysProfileControllerTest
{
    @Mock
    private ISysUserService userService;

    @Mock
    private TokenService tokenService;

    @InjectMocks
    private SysProfileController controller;

    @BeforeEach
    void installGuest()
    {
        LoginUser loginUser = new LoginUser(3L, null,
                user(3L, UserConstants.USER_TYPE_GUEST, UserConstants.GUEST_ROLE_KEY), Collections.emptySet());
        UsernamePasswordAuthenticationToken auth =
                new UsernamePasswordAuthenticationToken(loginUser, null, Collections.emptyList());
        SecurityContextHolder.getContext().setAuthentication(auth);
    }

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
    void guestUpdatePwdDeniedBeforeReset()
    {
        Map<String, String> params = new HashMap<>();
        params.put("oldPassword", "old");
        params.put("newPassword", "new");
        ServiceException ex = assertThrows(ServiceException.class, () -> controller.updatePwd(params));
        assertEquals("访客无法修改账号信息", ex.getMessage());
        verify(userService, never()).resetUserPwd(any(), any());
    }
}
