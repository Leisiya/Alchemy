package com.ruoyi.framework.interceptor;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

import com.github.pagehelper.PageHelper;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

class PageClearInterceptorTest
{
    @AfterEach
    void clearPageHelper()
    {
        PageHelper.clearPage();
    }

    @Test
    void afterCompletionClearsPageHelper() throws Exception
    {
        PageHelper.startPage(1, 20);
        assertNotNull(PageHelper.getLocalPage());

        new PageClearInterceptor().afterCompletion(null, null, null, null);

        assertNull(PageHelper.getLocalPage());
    }
}
