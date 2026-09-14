package com.ruoyi.web.controller.stock;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

import java.util.Collections;
import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.domain.entity.SysRole;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.system.domain.stock.StockScreenResult;
import com.ruoyi.system.domain.stock.StockWatchlist;
import com.ruoyi.system.service.IStockWatchlistService;
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
class StockWatchlistControllerTest
{
    @Mock
    private IStockWatchlistService service;

    @InjectMocks
    private StockWatchlistController controller;

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
    void guestAddDeniedBeforeService()
    {
        ServiceException ex = assertThrows(ServiceException.class, () -> controller.add(new StockWatchlist()));
        assertEquals("访客无法使用自选", ex.getMessage());
        verify(service, never()).add(any(), any());
    }

    @Test
    void guestCodesDeniedBeforeService()
    {
        ServiceException ex = assertThrows(ServiceException.class, () -> controller.codes());
        assertEquals("访客无法使用自选", ex.getMessage());
        verify(service, never()).selectCodes(any());
    }

    @Test
    void guestListDeniedBeforeService()
    {
        ServiceException ex = assertThrows(ServiceException.class, () -> controller.list(new StockScreenResult()));
        assertEquals("访客无法使用自选", ex.getMessage());
        verify(service, never()).selectList(any(), any());
    }

    @Test
    void guestRemoveDeniedBeforeService()
    {
        ServiceException ex = assertThrows(ServiceException.class, () -> controller.remove("000001.SZ"));
        assertEquals("访客无法使用自选", ex.getMessage());
        verify(service, never()).remove(any(), any());
    }
}
