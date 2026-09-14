package com.ruoyi.common.constant;

import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class JobWhitelistTest
{
    @Test
    void jobWhitelistIncludesQuartzAndWebTaskPackages()
    {
        assertTrue(java.util.Arrays.asList(Constants.JOB_WHITELIST_STR).contains("com.ruoyi.quartz.task"));
        assertTrue(java.util.Arrays.asList(Constants.JOB_WHITELIST_STR).contains("com.ruoyi.web.task"));
    }
}
