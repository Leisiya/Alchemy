package com.ruoyi.web.task;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import com.ruoyi.system.service.IStockScreeningService;

/**
 * 股票筛选定时任务
 */
@Component("stockScreeningTask")
public class StockScreeningTask
{
    private static final Logger log = LoggerFactory.getLogger(StockScreeningTask.class);

    @Autowired
    private IStockScreeningService stockScreeningService;

    public void refreshLatest()
    {
        log.info("Start stock screening refresh task");
        stockScreeningService.refreshLatest();
        log.info("Finish stock screening refresh task");
    }
}
