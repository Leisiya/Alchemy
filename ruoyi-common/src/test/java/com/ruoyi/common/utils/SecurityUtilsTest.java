package com.ruoyi.common.utils;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Collections;
import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.domain.entity.SysRole;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.exception.ServiceException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;

class SecurityUtilsTest
{
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
    void userTypeGuestIsGuest()
    {
        assertTrue(SecurityUtils.isGuest(user(3L, UserConstants.USER_TYPE_GUEST, "member_basic")));
    }

    @Test
    void guestRoleIsGuest()
    {
        assertTrue(SecurityUtils.isGuest(user(3L, UserConstants.USER_TYPE_SYS, UserConstants.GUEST_ROLE_KEY)));
    }

    @Test
    void memberBasicIsNotGuest()
    {
        assertFalse(SecurityUtils.isGuest(user(2L, UserConstants.USER_TYPE_SYS, "member_basic")));
    }

    @Test
    void adminIsNeverGuest()
    {
        assertFalse(SecurityUtils.isGuest(user(1L, UserConstants.USER_TYPE_GUEST, UserConstants.GUEST_ROLE_KEY)));
    }

    @Test
    void nullUserIsNotGuest()
    {
        assertFalse(SecurityUtils.isGuest((SysUser) null));
        assertFalse(SecurityUtils.isGuest((LoginUser) null));
        assertFalse(SecurityUtils.isGuest());
    }

    @Test
    void denyIfGuestThrowsConfiguredMessage()
    {
        SecurityUtils.denyIfGuest("访客无法使用自选");
        LoginUser loginUser = new LoginUser(3L, null,
                user(3L, UserConstants.USER_TYPE_GUEST, UserConstants.GUEST_ROLE_KEY), Collections.emptySet());
        UsernamePasswordAuthenticationToken auth =
                new UsernamePasswordAuthenticationToken(loginUser, null, Collections.emptyList());
        SecurityContextHolder.getContext().setAuthentication(auth);
        ServiceException ex = assertThrows(ServiceException.class, () -> SecurityUtils.denyIfGuest("访客无法使用自选"));
        assertEquals("访客无法使用自选", ex.getMessage());
    }
}
