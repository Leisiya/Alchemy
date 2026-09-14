package com.ruoyi.system.service.impl;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.system.domain.stock.ScreenResultSort;
import com.ruoyi.system.domain.stock.StockScreenResult;
import com.ruoyi.system.domain.stock.StockScreenRun;
import com.ruoyi.system.mapper.stock.StockScreenResultMapper;
import com.ruoyi.system.mapper.stock.StockScreenRunMapper;
import com.ruoyi.system.service.IStockScreeningService;

/**
 * 股票筛选服务实现：查询只读库；刷新通过 Python CLI 写库。
 */
@Service
public class StockScreeningServiceImpl implements IStockScreeningService
{
    private static final String STRATEGY_CODE = "HIGH_DIVIDEND_MA120";

    private static final int DASHBOARD_TOP_SIZE = 10;

    @Autowired
    private StockScreenRunMapper runMapper;

    @Autowired
    private StockScreenResultMapper resultMapper;

    @Autowired
    private PythonScreeningJobRunner pythonScreeningJobRunner;

    @Override
    public List<StockScreenResult> selectResultList(StockScreenResult query)
    {
        if (StringUtils.isEmpty(query.getTradeDate()))
        {
            StockScreenRun latestRun = selectLatestSuccessRunWithoutPaging();
            if (latestRun == null)
            {
                PageHelper.clearPage();
                return Collections.emptyList();
            }
            query.setTradeDate(latestRun.getTradeDate());
        }
        query.setStrategyCode(STRATEGY_CODE);
        ScreenResultSort.apply(query);
        return resultMapper.selectResultList(query);
    }

    @Override
    public List<String> selectTradeDateOptions()
    {
        return runMapper.selectSuccessTradeDates(STRATEGY_CODE);
    }

    @Override
    public StockScreenRun selectLatestSuccessRun()
    {
        return selectLatestSuccessRunWithoutPaging();
    }

    @Override
    public Map<String, Object> selectLatestDashboard()
    {
        Map<String, Object> dashboard = new LinkedHashMap<String, Object>();
        StockScreenRun latestSuccessRun = selectLatestSuccessRunWithoutPaging();
        dashboard.put("latestRun", latestSuccessRun);
        if (latestSuccessRun == null)
        {
            dashboard.put("lowTopList", Collections.emptyList());
            dashboard.put("highTopList", Collections.emptyList());
            return dashboard;
        }

        StockScreenResult lowQuery = new StockScreenResult();
        lowQuery.setTradeDate(latestSuccessRun.getTradeDate());
        lowQuery.setSignal("破位低估");
        lowQuery.setStrategyCode(STRATEGY_CODE);
        dashboard.put("lowTopList", subList(resultMapper.selectResultList(lowQuery), DASHBOARD_TOP_SIZE));

        StockScreenResult highQuery = new StockScreenResult();
        highQuery.setTradeDate(latestSuccessRun.getTradeDate());
        highQuery.setSignal("强势突破");
        highQuery.setStrategyCode(STRATEGY_CODE);
        dashboard.put("highTopList", subList(resultMapper.selectResultList(highQuery), DASHBOARD_TOP_SIZE));
        return dashboard;
    }

    @Override
    public void refreshLatest()
    {
        pythonScreeningJobRunner.run(null);
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

    private List<StockScreenResult> subList(List<StockScreenResult> list, int size)
    {
        if (list == null || list.isEmpty())
        {
            return Collections.emptyList();
        }
        return list.size() <= size ? list : new ArrayList<StockScreenResult>(list.subList(0, size));
    }
}
