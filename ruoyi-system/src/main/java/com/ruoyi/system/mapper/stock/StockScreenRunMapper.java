package com.ruoyi.system.mapper.stock;

import java.util.List;
import org.apache.ibatis.annotations.Param;
import com.ruoyi.system.domain.stock.StockScreenRun;

/**
 * 股票筛选运行快照 Mapper
 */
public interface StockScreenRunMapper
{
    public StockScreenRun selectByStrategyTradeDateAndStatus(@Param("strategyCode") String strategyCode, @Param("tradeDate") String tradeDate,
        @Param("status") String status);

    public StockScreenRun selectLatestSuccessRun(@Param("strategyCode") String strategyCode);

    public StockScreenRun selectLatestRun(@Param("strategyCode") String strategyCode);

    public List<String> selectSuccessTradeDates(@Param("strategyCode") String strategyCode);

    public int insertRun(StockScreenRun run);

    public int updateRun(StockScreenRun run);
}
