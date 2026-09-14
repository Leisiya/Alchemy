package com.ruoyi.system.domain.stock;

import java.math.BigDecimal;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.annotation.Excel.ColumnType;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 股票筛选结果 stock_screen_result
 */
public class StockScreenResult extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    private Long resultId;

    private Long runId;

    private String strategyCode;

    @Excel(name = "交易日")
    private String tradeDate;

    @Excel(name = "股票代码")
    private String tsCode;

    @Excel(name = "股票名称")
    private String name;

    @Excel(name = "行业")
    private String industry;

    @Excel(name = "PE", scale = 2)
    private BigDecimal peTtm;

    @Excel(name = "PB", scale = 2)
    private BigDecimal pb;

    @Excel(name = "ROE", scale = 2)
    private BigDecimal roe;

    @Excel(name = "股息率", scale = 2)
    private BigDecimal dvTtm;

    @Excel(name = "市值(亿元)", scale = 2)
    private BigDecimal totalMvYi;

    @Excel(name = "现价", scale = 2)
    private BigDecimal closePrice;

    @Excel(name = "MA120", scale = 2)
    private BigDecimal ma120;

    @Excel(name = "现价/MA120", scale = 4, cellType = ColumnType.NUMERIC)
    private BigDecimal priceMa120Ratio;

    @Excel(name = "信号", width = 18, handler = Ma120SignalDisplay.class)
    private String ma120Signal;

    private Boolean outOfPool;

    private String signal;

    private BigDecimal peTtmMin;

    private BigDecimal peTtmMax;

    private BigDecimal pbMin;

    private BigDecimal pbMax;

    private BigDecimal roeMin;

    private BigDecimal roeMax;

    private BigDecimal dvTtmMin;

    private BigDecimal dvTtmMax;

    private BigDecimal totalMvYiMin;

    private BigDecimal totalMvYiMax;

    private BigDecimal closePriceMin;

    private BigDecimal closePriceMax;

    private BigDecimal ma120Min;

    private BigDecimal ma120Max;

    private BigDecimal priceMa120RatioMin;

    private BigDecimal priceMa120RatioMax;

    private String sortBy;

    private String sortOrder;

    private String safeOrderBy;

    public Long getResultId()
    {
        return resultId;
    }

    public void setResultId(Long resultId)
    {
        this.resultId = resultId;
    }

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

    public BigDecimal getPeTtm()
    {
        return peTtm;
    }

    public void setPeTtm(BigDecimal peTtm)
    {
        this.peTtm = peTtm;
    }

    public BigDecimal getPb()
    {
        return pb;
    }

    public void setPb(BigDecimal pb)
    {
        this.pb = pb;
    }

    public BigDecimal getRoe()
    {
        return roe;
    }

    public void setRoe(BigDecimal roe)
    {
        this.roe = roe;
    }

    public BigDecimal getDvTtm()
    {
        return dvTtm;
    }

    public void setDvTtm(BigDecimal dvTtm)
    {
        this.dvTtm = dvTtm;
    }

    public BigDecimal getTotalMvYi()
    {
        return totalMvYi;
    }

    public void setTotalMvYi(BigDecimal totalMvYi)
    {
        this.totalMvYi = totalMvYi;
    }

    public BigDecimal getClosePrice()
    {
        return closePrice;
    }

    public void setClosePrice(BigDecimal closePrice)
    {
        this.closePrice = closePrice;
    }

    public BigDecimal getMa120()
    {
        return ma120;
    }

    public void setMa120(BigDecimal ma120)
    {
        this.ma120 = ma120;
    }

    public BigDecimal getPriceMa120Ratio()
    {
        return priceMa120Ratio;
    }

    public void setPriceMa120Ratio(BigDecimal priceMa120Ratio)
    {
        this.priceMa120Ratio = priceMa120Ratio;
    }

    public String getMa120Signal()
    {
        return ma120Signal;
    }

    public void setMa120Signal(String ma120Signal)
    {
        this.ma120Signal = ma120Signal;
    }

    public Boolean getOutOfPool()
    {
        return outOfPool;
    }

    public void setOutOfPool(Boolean outOfPool)
    {
        this.outOfPool = outOfPool;
    }

    public String getSignal()
    {
        return signal;
    }

    public void setSignal(String signal)
    {
        this.signal = signal;
    }

    public BigDecimal getPeTtmMin()
    {
        return peTtmMin;
    }

    public void setPeTtmMin(BigDecimal peTtmMin)
    {
        this.peTtmMin = peTtmMin;
    }

    public BigDecimal getPeTtmMax()
    {
        return peTtmMax;
    }

    public void setPeTtmMax(BigDecimal peTtmMax)
    {
        this.peTtmMax = peTtmMax;
    }

    public BigDecimal getPbMin()
    {
        return pbMin;
    }

    public void setPbMin(BigDecimal pbMin)
    {
        this.pbMin = pbMin;
    }

    public BigDecimal getPbMax()
    {
        return pbMax;
    }

    public void setPbMax(BigDecimal pbMax)
    {
        this.pbMax = pbMax;
    }

    public BigDecimal getRoeMin()
    {
        return roeMin;
    }

    public void setRoeMin(BigDecimal roeMin)
    {
        this.roeMin = roeMin;
    }

    public BigDecimal getRoeMax()
    {
        return roeMax;
    }

    public void setRoeMax(BigDecimal roeMax)
    {
        this.roeMax = roeMax;
    }

    public BigDecimal getDvTtmMin()
    {
        return dvTtmMin;
    }

    public void setDvTtmMin(BigDecimal dvTtmMin)
    {
        this.dvTtmMin = dvTtmMin;
    }

    public BigDecimal getDvTtmMax()
    {
        return dvTtmMax;
    }

    public void setDvTtmMax(BigDecimal dvTtmMax)
    {
        this.dvTtmMax = dvTtmMax;
    }

    public BigDecimal getTotalMvYiMin()
    {
        return totalMvYiMin;
    }

    public void setTotalMvYiMin(BigDecimal totalMvYiMin)
    {
        this.totalMvYiMin = totalMvYiMin;
    }

    public BigDecimal getTotalMvYiMax()
    {
        return totalMvYiMax;
    }

    public void setTotalMvYiMax(BigDecimal totalMvYiMax)
    {
        this.totalMvYiMax = totalMvYiMax;
    }

    public BigDecimal getClosePriceMin()
    {
        return closePriceMin;
    }

    public void setClosePriceMin(BigDecimal closePriceMin)
    {
        this.closePriceMin = closePriceMin;
    }

    public BigDecimal getClosePriceMax()
    {
        return closePriceMax;
    }

    public void setClosePriceMax(BigDecimal closePriceMax)
    {
        this.closePriceMax = closePriceMax;
    }

    public BigDecimal getMa120Min()
    {
        return ma120Min;
    }

    public void setMa120Min(BigDecimal ma120Min)
    {
        this.ma120Min = ma120Min;
    }

    public BigDecimal getMa120Max()
    {
        return ma120Max;
    }

    public void setMa120Max(BigDecimal ma120Max)
    {
        this.ma120Max = ma120Max;
    }

    public BigDecimal getPriceMa120RatioMin()
    {
        return priceMa120RatioMin;
    }

    public void setPriceMa120RatioMin(BigDecimal priceMa120RatioMin)
    {
        this.priceMa120RatioMin = priceMa120RatioMin;
    }

    public BigDecimal getPriceMa120RatioMax()
    {
        return priceMa120RatioMax;
    }

    public void setPriceMa120RatioMax(BigDecimal priceMa120RatioMax)
    {
        this.priceMa120RatioMax = priceMa120RatioMax;
    }

    public String getSortBy()
    {
        return sortBy;
    }

    public void setSortBy(String sortBy)
    {
        this.sortBy = sortBy;
    }

    public String getSortOrder()
    {
        return sortOrder;
    }

    public void setSortOrder(String sortOrder)
    {
        this.sortOrder = sortOrder;
    }

    public String getSafeOrderBy()
    {
        return safeOrderBy;
    }

    public void setSafeOrderBy(String safeOrderBy)
    {
        this.safeOrderBy = safeOrderBy;
    }

    @Override
    public String toString()
    {
        return new ToStringBuilder(this, ToStringStyle.MULTI_LINE_STYLE)
            .append("resultId", getResultId())
            .append("runId", getRunId())
            .append("strategyCode", getStrategyCode())
            .append("tradeDate", getTradeDate())
            .append("tsCode", getTsCode())
            .append("name", getName())
            .append("industry", getIndustry())
            .append("peTtm", getPeTtm())
            .append("pb", getPb())
            .append("roe", getRoe())
            .append("dvTtm", getDvTtm())
            .append("totalMvYi", getTotalMvYi())
            .append("closePrice", getClosePrice())
            .append("ma120", getMa120())
            .append("priceMa120Ratio", getPriceMa120Ratio())
            .append("ma120Signal", getMa120Signal())
            .append("outOfPool", getOutOfPool())
            .append("createTime", getCreateTime())
            .toString();
    }
}
