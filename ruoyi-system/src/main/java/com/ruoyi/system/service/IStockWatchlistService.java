package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.system.domain.stock.StockScreenResult;

/**
 * 用户自选股服务
 */
public interface IStockWatchlistService
{
    public List<String> selectCodes(Long userId);

    public List<StockScreenResult> selectList(Long userId, StockScreenResult query);

    public void add(Long userId, String tsCode);

    public void remove(Long userId, String tsCode);
}
