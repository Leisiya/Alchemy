package com.ruoyi.web.controller.system;

import static org.mockito.Mockito.verify;

import java.util.Collections;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.system.service.ISysNoticeReadService;
import com.ruoyi.system.service.ISysNoticeService;
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
class SysNoticeControllerTest
{
    @Mock
    private ISysNoticeService noticeService;

    @Mock
    private ISysNoticeReadService noticeReadService;

    @InjectMocks
    private SysNoticeController controller;

    @BeforeEach
    void installAdmin()
    {
        SysUser user = new SysUser(1L);
        LoginUser loginUser = new LoginUser(1L, null, user, Collections.emptySet());
        SecurityContextHolder.getContext().setAuthentication(
            new UsernamePasswordAuthenticationToken(loginUser, null, Collections.emptyList()));
    }

    @AfterEach
    void clear()
    {
        SecurityContextHolder.clearContext();
    }

    @Test
    void removeAlsoDeletesReadRows()
    {
        Long[] ids = new Long[] { 1L, 2L };
        controller.remove(ids);
        verify(noticeService).deleteNoticeByIds(ids);
        verify(noticeReadService).deleteByNoticeIds(ids);
    }
}
