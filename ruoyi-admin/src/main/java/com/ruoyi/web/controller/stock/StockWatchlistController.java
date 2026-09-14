package com.ruoyi.web.controller.stock;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.common.utils.SecurityUtils;
import com.ruoyi.system.domain.stock.StockScreenResult;
import com.ruoyi.system.domain.stock.StockWatchlist;
import com.ruoyi.system.service.IStockWatchlistService;

/**
 * 用户自选股
 */
@RestController
@RequestMapping("/stock/watchlist")
public class StockWatchlistController extends BaseController
{
    @Autowired
    private IStockWatchlistService stockWatchlistService;

    @PreAuthorize("@ss.hasPermi('stock:screener:list')")
    @GetMapping("/list")
    public TableDataInfo list(StockScreenResult query)
    {
        SecurityUtils.denyIfGuest("访客无法使用自选");
        startPage();
        List<StockScreenResult> list = stockWatchlistService.selectList(getUserId(), query);
        return getDataTable(list);
    }

    @PreAuthorize("@ss.hasPermi('stock:screener:list')")
    @GetMapping("/codes")
    public AjaxResult codes()
    {
        SecurityUtils.denyIfGuest("访客无法使用自选");
        return success(stockWatchlistService.selectCodes(getUserId()));
    }

    @PreAuthorize("@ss.hasPermi('stock:screener:list')")
    @PostMapping
    public AjaxResult add(@RequestBody StockWatchlist body)
    {
        SecurityUtils.denyIfGuest("访客无法使用自选");
        stockWatchlistService.add(getUserId(), body == null ? null : body.getTsCode());
        return success();
    }

    @PreAuthorize("@ss.hasPermi('stock:screener:list')")
    @DeleteMapping("/{tsCode:.+}")
    public AjaxResult remove(@PathVariable String tsCode)
    {
        SecurityUtils.denyIfGuest("访客无法使用自选");
        stockWatchlistService.remove(getUserId(), tsCode);
        return success();
    }
}
