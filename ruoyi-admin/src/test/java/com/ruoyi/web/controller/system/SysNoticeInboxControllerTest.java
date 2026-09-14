package com.ruoyi.web.controller.system;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Collections;
import java.util.List;
import com.ruoyi.common.constant.UserConstants;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.domain.entity.SysRole;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.system.domain.SysNotice;
import com.ruoyi.system.service.ISysNoticeReadService;
import com.ruoyi.system.service.ISysNoticeService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;

@ExtendWith(MockitoExtension.class)
class SysNoticeInboxControllerTest
{
    @Mock
    private ISysNoticeReadService noticeReadService;

    @Mock
    private ISysNoticeService noticeService;

    @InjectMocks
    private SysNoticeInboxController controller;

    @AfterEach
    void clearSecurityContext()
    {
        SecurityContextHolder.clearContext();
    }

    private void install(Long userId, String type, String roleKey)
    {
        LoginUser loginUser = new LoginUser(userId, null,
                user(userId, type, roleKey), Collections.emptySet());
        UsernamePasswordAuthenticationToken auth =
                new UsernamePasswordAuthenticationToken(loginUser, null, Collections.emptyList());
        SecurityContextHolder.getContext().setAuthentication(auth);
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
    void guestMarkReadDoesNotWriteDatabase()
    {
        install(3L, UserConstants.USER_TYPE_GUEST, UserConstants.GUEST_ROLE_KEY);
        AjaxResult result = controller.markRead(9L);
        assertEquals(200, result.get(AjaxResult.CODE_TAG));
        verify(noticeReadService, never()).markRead(anyLong(), anyLong());
    }

    @Test
    void guestMarkAllReadDoesNotWriteDatabase()
    {
        install(3L, UserConstants.USER_TYPE_GUEST, UserConstants.GUEST_ROLE_KEY);
        controller.markAllRead();
        verify(noticeReadService, never()).markAllRead(anyLong());
        verify(noticeReadService, never()).markReadBatch(anyLong(), any());
    }

    @Test
    void guestInboxForcesUnread()
    {
        install(3L, UserConstants.USER_TYPE_GUEST, UserConstants.GUEST_ROLE_KEY);
        SysNotice row = new SysNotice();
        row.setNoticeId(1L);
        row.setIsRead(true);
        when(noticeReadService.selectNoticeListWithReadStatus(3L, 50))
            .thenReturn(Collections.singletonList(row));
        AjaxResult result = controller.inbox();
        @SuppressWarnings("unchecked")
        List<SysNotice> data = (List<SysNotice>) result.get(AjaxResult.DATA_TAG);
        assertFalse(data.get(0).getIsRead());
    }

    @Test
    void guestUnreadCountUsesPublishedCount()
    {
        install(3L, UserConstants.USER_TYPE_GUEST, UserConstants.GUEST_ROLE_KEY);
        when(noticeService.selectPublishedCount()).thenReturn(4);
        AjaxResult result = controller.unreadCount();
        assertEquals(4, result.get(AjaxResult.DATA_TAG));
        verify(noticeReadService, never()).selectUnreadCount(anyLong());
    }

    @Test
    void memberMarkReadWritesDatabase()
    {
        install(2L, UserConstants.USER_TYPE_SYS, "member_basic");
        controller.markRead(9L);
        verify(noticeReadService).markRead(9L, 2L);
    }

    @Test
    void memberUnreadCountUsesReadTable()
    {
        install(2L, UserConstants.USER_TYPE_SYS, "member_basic");
        when(noticeReadService.selectUnreadCount(2L)).thenReturn(3);
        AjaxResult result = controller.unreadCount();
        assertEquals(3, result.get(AjaxResult.DATA_TAG));
        verify(noticeService, never()).selectPublishedCount();
    }
}
