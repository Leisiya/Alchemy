package com.ruoyi.system.domain.stock;

import java.util.Date;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 股票筛选运行快照 stock_screen_run
 */
public class StockScreenRun extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    private Long runId;

    private String strategyCode;

    private String tradeDate;

    private String status;

    private Integer totalCount;

    private Integer lowCount;

    private Integer highCount;

    private String errorMessage;

    private Date startedAt;

    private Date finishedAt;

    public Long getRunId()
    {
        return runId;
    }

    public void setRunId(Long runId)
    {
        this.runId = runId;
    }

    public String getStrategyCode()
    {
        return strategyCode;
    }

    public void setStrategyCode(String strategyCode)
    {
        this.strategyCode = strategyCode;
    }

    public String getTradeDate()
    {
        return tradeDate;
    }

    public void setTradeDate(String tradeDate)
    {
        this.tradeDate = tradeDate;
    }

    public String getStatus()
    {
        return status;
    }

    public void setStatus(String status)
    {
        this.status = status;
    }

    public Integer getTotalCount()
    {
        return totalCount;
    }

    public void setTotalCount(Integer totalCount)
    {
        this.totalCount = totalCount;
    }

    public Integer getLowCount()
    {
        return lowCount;
    }

    public void setLowCount(Integer lowCount)
    {
        this.lowCount = lowCount;
    }

    public Integer getHighCount()
    {
        return highCount;
    }

    public void setHighCount(Integer highCount)
    {
        this.highCount = highCount;
    }

    public String getErrorMessage()
    {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage)
    {
        this.errorMessage = errorMessage;
    }

    public Date getStartedAt()
    {
        return startedAt;
    }

    public void setStartedAt(Date startedAt)
    {
        this.startedAt = startedAt;
    }

    public Date getFinishedAt()
    {
        return finishedAt;
    }

    public void setFinishedAt(Date finishedAt)
    {
        this.finishedAt = finishedAt;
    }

    @Override
    public String toString()
    {
        return new ToStringBuilder(this, ToStringStyle.MULTI_LINE_STYLE)
            .append("runId", getRunId())
            .append("strategyCode", getStrategyCode())
            .append("tradeDate", getTradeDate())
            .append("status", getStatus())
            .append("totalCount", getTotalCount())
            .append("lowCount", getLowCount())
            .append("highCount", getHighCount())
            .append("errorMessage", getErrorMessage())
            .append("startedAt", getStartedAt())
            .append("finishedAt", getFinishedAt())
            .append("createTime", getCreateTime())
            .append("updateTime", getUpdateTime())
            .toString();
    }
}
