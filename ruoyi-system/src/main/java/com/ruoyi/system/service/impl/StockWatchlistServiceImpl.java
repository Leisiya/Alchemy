package com.ruoyi.system.service.impl;

import java.util.Date;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.system.domain.stock.ScreenResultSort;
import com.ruoyi.system.domain.stock.StockScreenResult;
import com.ruoyi.system.domain.stock.StockScreenRun;
import com.ruoyi.system.domain.stock.StockWatchlist;
import com.ruoyi.system.mapper.stock.StockScreenResultMapper;
import com.ruoyi.system.mapper.stock.StockScreenRunMapper;
import com.ruoyi.system.mapper.stock.StockWatchlistMapper;
import com.ruoyi.system.service.IStockWatchlistService;

/**
 * 用户自选股服务实现
 */
@Service
public class StockWatchlistServiceImpl implements IStockWatchlistService
{
    private static final String STRATEGY_CODE = "HIGH_DIVIDEND_MA120";

    private static final int MAX_SIZE = 200;

    @Autowired
    private StockScreenRunMapper runMapper;

    @Autowired
    private StockScreenResultMapper resultMapper;

    @Autowired
    private StockWatchlistMapper watchlistMapper;

    @Override
    public List<String> selectCodes(Long userId)
    {
        return watchlistMapper.selectCodesByUserId(userId);
    }

    @Override
    public List<StockScreenResult> selectList(Long userId, StockScreenResult query)
    {
        StockScreenRun latestRun = selectLatestSuccessRunWithoutPaging();
        Long runId = latestRun == null ? null : latestRun.getRunId();
        ScreenResultSort.applyWatchlist(query);
        return watchlistMapper.selectWatchlistJoined(userId, runId, query);
    }

    @Override
    public void add(Long userId, String tsCode)
    {
        if (tsCode == null || tsCode.trim().isEmpty())
        {
            throw new ServiceException("股票代码不能为空");
        }

        StockScreenRun latestRun = selectLatestSuccessRunWithoutPaging();
        if (latestRun == null)
        {
            throw new ServiceException("暂无成功的筛股快照，无法加入自选");
        }

        StockScreenResult snapshot = resultMapper.selectByRunIdAndTsCode(latestRun.getRunId(), tsCode);
        if (snapshot == null)
        {
            throw new ServiceException("该股票不在当前候选池中");
        }

        if (watchlistMapper.selectByUserIdAndTsCode(userId, tsCode) != null)
        {
            throw new ServiceException("已在自选中");
        }

        if (watchlistMapper.countByUserId(userId) >= MAX_SIZE)
        {
            throw new ServiceException("自选最多 200 只");
        }

        StockWatchlist row = new StockWatchlist();
        row.setUserId(userId);
        row.setTsCode(tsCode);
        row.setName(snapshot.getName());
        row.setIndustry(snapshot.getIndustry());
        row.setCreateTime(new Date());
        watchlistMapper.insertWatchlist(row);
    }

    @Override
    public void remove(Long userId, String tsCode)
    {
        if (watchlistMapper.deleteByUserIdAndTsCode(userId, tsCode) == 0)
        {
            throw new ServiceException("该股票不在自选中");
        }
    }

    /**
     * 列表接口会先 PageHelper.startPage，再进本方法。若此时执行带 limit 1 的快照查询，
     * 拦截器会再拼一个 LIMIT，生成非法 SQL：{@code limit 1 LIMIT ?}。
     */
    private StockScreenRun selectLatestSuccessRunWithoutPaging()
    {
        Page<?> page = PageHelper.getLocalPage();
        try
        {
            PageHelper.clearPage();
            return runMapper.selectLatestSuccessRun(STRATEGY_CODE);
        }
        finally
        {
            if (page != null)
            {
                PageHelper.startPage(page.getPageNum(), page.getPageSize(), page.getOrderBy())
                    .setReasonable(page.getReasonable());
            }
        }
    }
}
