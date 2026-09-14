package com.ruoyi.system.service;

import java.util.List;
import java.util.Map;
import com.ruoyi.system.domain.stock.StockScreenResult;
import com.ruoyi.system.domain.stock.StockScreenRun;

/**
 * 股票筛选服务
 */
public interface IStockScreeningService
{
    public List<StockScreenResult> selectResultList(StockScreenResult query);

    public List<String> selectTradeDateOptions();

    public StockScreenRun selectLatestSuccessRun();

    public Map<String, Object> selectLatestDashboard();

    public void refreshLatest();
}
