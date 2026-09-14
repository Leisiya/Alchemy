package com.ruoyi.system.domain.stock;

import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 用户自选股 stock_watchlist
 */
public class StockWatchlist extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    private Long watchlistId;

    private Long userId;

    private String tsCode;

    private String name;

    private String industry;

    public Long getWatchlistId()
    {
        return watchlistId;
    }

    public void setWatchlistId(Long watchlistId)
    {
        this.watchlistId = watchlistId;
    }

    public Long getUserId()
    {
        return userId;
    }

    public void setUserId(Long userId)
    {
        this.userId = userId;
    }

    public String getTsCode()
    {
        return tsCode;
    }

    public void setTsCode(String tsCode)
    {
        this.tsCode = tsCode;
    }

    public String getName()
    {
        return name;
    }

    public void setName(String name)
    {
        this.name = name;
    }

    public String getIndustry()
    {
        return industry;
    }

    public void setIndustry(String industry)
    {
        this.industry = industry;
    }
}
