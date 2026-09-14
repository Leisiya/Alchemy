package com.ruoyi.system.domain.stock;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import org.junit.jupiter.api.Test;

class ScreenResultSortTest
{
    @Test
    void listDefaultIsDividendThenCode()
    {
        assertEquals("dv_ttm desc, ts_code asc", ScreenResultSort.resolveList(null, null, null));
        assertEquals("dv_ttm desc, ts_code asc", ScreenResultSort.resolveList("", "desc", ""));
    }

    @Test
    void undervaluedDefaultIsRatioAsc()
    {
        assertEquals("price_ma120_ratio asc, dv_ttm desc, ts_code asc",
            ScreenResultSort.resolveList(null, null, "破位低估"));
    }

    @Test
    void breakoutDefaultIsRatioDesc()
    {
        assertEquals("price_ma120_ratio desc, dv_ttm desc, ts_code asc",
            ScreenResultSort.resolveList(null, null, "强势突破"));
    }

    @Test
    void watchlistDefaultIsCreateTime()
    {
        assertEquals("w.create_time desc, w.ts_code asc",
            ScreenResultSort.resolveWatchlist(null, null));
    }

    @Test
    void validListSortPutsNullsLastThenCode()
    {
        assertEquals("pe_ttm is null, pe_ttm asc, ts_code asc",
            ScreenResultSort.resolveList("peTtm", "asc", "破位低估"));
        assertEquals("dv_ttm is null, dv_ttm desc, ts_code asc",
            ScreenResultSort.resolveList("dvTtm", "DESC", null));
        assertEquals("price_ma120_ratio is null, price_ma120_ratio desc, ts_code asc",
            ScreenResultSort.resolveList("priceMa120Ratio", "desc", "强势突破"));
    }

    @Test
    void validWatchlistSortPrefixesResultColumns()
    {
        assertEquals("r.total_mv_yi is null, r.total_mv_yi desc, w.ts_code asc",
            ScreenResultSort.resolveWatchlist("totalMvYi", "desc"));
    }

    @Test
    void unknownOrUnsafeSortByFallsBack()
    {
        assertEquals("dv_ttm desc, ts_code asc",
            ScreenResultSort.resolveList("name", "desc", null));
        assertEquals("dv_ttm desc, ts_code asc",
            ScreenResultSort.resolveList("pe_ttm;drop table", "desc", null));
        assertEquals("w.create_time desc, w.ts_code asc",
            ScreenResultSort.resolveWatchlist("tsCode", "asc"));
    }

    @Test
    void illegalSortOrderFallsBackEvenWhenColumnIsValid()
    {
        assertEquals("price_ma120_ratio desc, dv_ttm desc, ts_code asc",
            ScreenResultSort.resolveList("peTtm", "descending", "强势突破"));
        assertEquals("dv_ttm desc, ts_code asc",
            ScreenResultSort.resolveList("peTtm", "", null));
        assertEquals("w.create_time desc, w.ts_code asc",
            ScreenResultSort.resolveWatchlist("pb", "ascending"));
    }

    @Test
    void applyWritesSafeOrderByAndIgnoresNullQuery()
    {
        StockScreenResult query = new StockScreenResult();
        query.setSortBy("roe");
        query.setSortOrder("asc");
        ScreenResultSort.apply(query);
        assertEquals("roe is null, roe asc, ts_code asc", query.getSafeOrderBy());

        StockScreenResult watch = new StockScreenResult();
        watch.setSortBy("closePrice");
        watch.setSortOrder("desc");
        ScreenResultSort.applyWatchlist(watch);
        assertEquals("r.close_price is null, r.close_price desc, w.ts_code asc", watch.getSafeOrderBy());

        ScreenResultSort.apply(null);
        ScreenResultSort.applyWatchlist(null);
        assertNull(new StockScreenResult().getSafeOrderBy());
    }
}
