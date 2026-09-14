package com.ruoyi.system.domain.stock;

import java.util.Collections;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

public final class ScreenResultSort
{
    private static final Map<String, String> COLUMNS;

    static
    {
        Map<String, String> columns = new HashMap<String, String>();
        columns.put("peTtm", "pe_ttm");
        columns.put("pb", "pb");
        columns.put("roe", "roe");
        columns.put("dvTtm", "dv_ttm");
        columns.put("totalMvYi", "total_mv_yi");
        columns.put("closePrice", "close_price");
        columns.put("ma120", "ma120");
        columns.put("priceMa120Ratio", "price_ma120_ratio");
        COLUMNS = Collections.unmodifiableMap(columns);
    }

    private ScreenResultSort()
    {
    }

    public static String resolveList(String sortBy, String sortOrder, String signal)
    {
        String column = COLUMNS.get(sortBy);
        String direction = direction(sortOrder);
        if (column == null || direction == null)
        {
            return defaultList(signal);
        }
        return column + " is null, " + column + " " + direction + ", ts_code asc";
    }

    public static String resolveWatchlist(String sortBy, String sortOrder)
    {
        String column = COLUMNS.get(sortBy);
        String direction = direction(sortOrder);
        if (column == null || direction == null)
        {
            return "w.create_time desc, w.ts_code asc";
        }
        String qualified = "r." + column;
        return qualified + " is null, " + qualified + " " + direction + ", w.ts_code asc";
    }

    public static void apply(StockScreenResult query)
    {
        if (query == null)
        {
            return;
        }
        query.setSafeOrderBy(resolveList(query.getSortBy(), query.getSortOrder(), query.getSignal()));
    }

    public static void applyWatchlist(StockScreenResult query)
    {
        if (query == null)
        {
            return;
        }
        query.setSafeOrderBy(resolveWatchlist(query.getSortBy(), query.getSortOrder()));
    }

    private static String direction(String sortOrder)
    {
        if (sortOrder == null)
        {
            return null;
        }
        String normalized = sortOrder.trim().toLowerCase(Locale.ROOT);
        if ("asc".equals(normalized) || "desc".equals(normalized))
        {
            return normalized;
        }
        return null;
    }

    private static String defaultList(String signal)
    {
        if ("破位低估".equals(signal))
        {
            return "price_ma120_ratio asc, dv_ttm desc, ts_code asc";
        }
        if ("强势突破".equals(signal))
        {
            return "price_ma120_ratio desc, dv_ttm desc, ts_code asc";
        }
        return "dv_ttm desc, ts_code asc";
    }
}
