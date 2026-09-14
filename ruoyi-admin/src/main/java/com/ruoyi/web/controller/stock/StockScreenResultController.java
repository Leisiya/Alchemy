package com.ruoyi.web.controller.stock;

import java.util.List;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.annotation.Log;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.core.page.TableDataInfo;
import com.ruoyi.common.enums.BusinessType;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.system.domain.stock.StockScreenResult;
import com.ruoyi.system.service.IStockScreeningService;

/**
 * 股票筛选结果
 */
@RestController
@RequestMapping("/stock/screener")
public class StockScreenResultController extends BaseController
{
    @Autowired
    private IStockScreeningService stockScreeningService;

    @PreAuthorize("@ss.hasPermi('stock:screener:list')")
    @GetMapping("/results/list")
    public TableDataInfo list(StockScreenResult query)
    {
        startPage();
        List<StockScreenResult> list = stockScreeningService.selectResultList(query);
        return getDataTable(list);
    }

    @Log(title = "股票筛选", businessType = BusinessType.EXPORT)
    @PreAuthorize("@ss.hasPermi('stock:screener:export')")
    @PostMapping("/results/export")
    public void export(HttpServletResponse response, StockScreenResult query)
    {
        List<StockScreenResult> list = stockScreeningService.selectResultList(query);
        ExcelUtil<StockScreenResult> util = new ExcelUtil<StockScreenResult>(StockScreenResult.class);
        util.exportExcel(response, list, "筛股结果");
    }

    @PreAuthorize("@ss.hasPermi('stock:screener:query')")
    @GetMapping("/runs/options")
    public AjaxResult options()
    {
        AjaxResult ajax = AjaxResult.success();
        ajax.put("tradeDates", stockScreeningService.selectTradeDateOptions());
        return ajax;
    }

    @PreAuthorize("@ss.hasPermi('stock:screener:query')")
    @GetMapping("/runs/latest")
    public AjaxResult latest()
    {
        return success(stockScreeningService.selectLatestSuccessRun());
    }

    @PreAuthorize("@ss.hasPermi('stock:screener:query')")
    @GetMapping("/dashboard/latest")
    public AjaxResult dashboard()
    {
        return success(stockScreeningService.selectLatestDashboard());
    }
}
