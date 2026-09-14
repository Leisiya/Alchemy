package com.ruoyi.system.mapper.stock;

import java.util.List;
import org.apache.ibatis.annotations.Param;
import com.ruoyi.system.domain.stock.StockScreenResult;

/**
 * 股票筛选结果 Mapper
 */
public interface StockScreenResultMapper
{
    public List<StockScreenResult> selectResultList(StockScreenResult query);

    public StockScreenResult selectByRunIdAndTsCode(@Param("runId") Long runId, @Param("tsCode") String tsCode);

    public int deleteByRunId(Long runId);

    public int insertBatch(List<StockScreenResult> list);
}
