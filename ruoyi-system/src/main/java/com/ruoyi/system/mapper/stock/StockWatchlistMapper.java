package com.ruoyi.system.mapper.stock;

import java.util.List;
import org.apache.ibatis.annotations.Param;
import com.ruoyi.system.domain.stock.StockScreenResult;
import com.ruoyi.system.domain.stock.StockWatchlist;

/**
 * 用户自选股 Mapper
 */
public interface StockWatchlistMapper
{
    public int insertWatchlist(StockWatchlist row);

    public int deleteByUserIdAndTsCode(@Param("userId") Long userId, @Param("tsCode") String tsCode);

    public int countByUserId(@Param("userId") Long userId);

    public List<String> selectCodesByUserId(@Param("userId") Long userId);

    public StockWatchlist selectByUserIdAndTsCode(@Param("userId") Long userId, @Param("tsCode") String tsCode);

    public List<StockScreenResult> selectWatchlistJoined(@Param("userId") Long userId, @Param("runId") Long runId,
        @Param("query") StockScreenResult query);
}
