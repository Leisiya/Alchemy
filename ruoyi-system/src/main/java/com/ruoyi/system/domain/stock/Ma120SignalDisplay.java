package com.ruoyi.system.domain.stock;

import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.Workbook;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.common.utils.poi.ExcelHandlerAdapter;

/**
 * MA120 信号导出展示：空值显示「有待观察」，不改库存值。
 */
public class Ma120SignalDisplay implements ExcelHandlerAdapter
{
    public static final String PENDING_OBSERVATION = "有待观察";

    public static String label(String ma120Signal)
    {
        if (StringUtils.isEmpty(ma120Signal))
        {
            return PENDING_OBSERVATION;
        }
        return ma120Signal;
    }

    @Override
    public Object format(Object value, String[] args, Cell cell, Workbook wb)
    {
        return label(value == null ? null : value.toString());
    }
}
