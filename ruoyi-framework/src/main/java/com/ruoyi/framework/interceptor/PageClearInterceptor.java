package com.ruoyi.framework.interceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;
import com.ruoyi.common.utils.PageUtils;

/**
 * 请求结束后清掉 PageHelper 线程变量，避免 Tomcat 线程复用时把分页拼到下一次查询。
 */
@Component
public class PageClearInterceptor implements HandlerInterceptor
{
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex)
    {
        PageUtils.clearPage();
    }
}
