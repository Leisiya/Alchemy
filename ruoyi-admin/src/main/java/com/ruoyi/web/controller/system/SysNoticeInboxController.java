package com.ruoyi.web.controller.system;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.system.domain.SysNotice;
import com.ruoyi.system.service.ISysNoticeReadService;
import com.ruoyi.system.service.ISysNoticeService;

/**
 * 登录用户通知收件箱
 *
 * @author ruoyi
 */
@RestController
@RequestMapping("/system/notice")
public class SysNoticeInboxController extends BaseController
{
    public static final int INBOX_LIMIT = 50;

    @Autowired
    private ISysNoticeReadService noticeReadService;

    @Autowired
    private ISysNoticeService noticeService;

    @GetMapping("/inbox")
    public AjaxResult inbox()
    {
        List<SysNotice> list = noticeReadService.selectNoticeListWithReadStatus(getUserId(), INBOX_LIMIT);
        if (SecurityUtils.isGuest())
        {
            for (SysNotice item : list)
            {
                item.setIsRead(false);
            }
        }
        return success(list);
    }

    @GetMapping("/unread-count")
    public AjaxResult unreadCount()
    {
        if (SecurityUtils.isGuest())
        {
            return success(noticeService.selectPublishedCount());
        }
        return success(noticeReadService.selectUnreadCount(getUserId()));
    }

    @PutMapping("/read/{noticeId}")
    public AjaxResult markRead(@PathVariable Long noticeId)
    {
        if (!SecurityUtils.isGuest())
        {
            noticeReadService.markRead(noticeId, getUserId());
        }
        return success();
    }

    @PutMapping("/read-all")
    public AjaxResult markAllRead()
    {
        if (!SecurityUtils.isGuest())
        {
            noticeReadService.markAllRead(getUserId());
        }
        return success();
    }
}
