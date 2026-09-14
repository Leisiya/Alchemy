package com.ruoyi.system.service.impl;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import com.github.pagehelper.PageHelper;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.system.domain.stock.StockScreenResult;
import com.ruoyi.system.domain.stock.StockScreenRun;
import com.ruoyi.system.domain.stock.StockWatchlist;
import com.ruoyi.system.mapper.stock.StockScreenResultMapper;
import com.ruoyi.system.mapper.stock.StockScreenRunMapper;
import com.ruoyi.system.mapper.stock.StockWatchlistMapper;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class StockWatchlistServiceImplTest
{
    @Mock
    private StockScreenRunMapper runMapper;

    @Mock
    private StockScreenResultMapper resultMapper;

    @Mock
    private StockWatchlistMapper watchlistMapper;

    @InjectMocks
    private StockWatchlistServiceImpl service;

    @AfterEach
    void clearPageHelper()
    {
        PageHelper.clearPage();
    }

    private StockScreenRun successRun()
    {
        StockScreenRun run = new StockScreenRun();
        run.setRunId(9L);
        run.setTradeDate("20260818");
        return run;
    }

    private StockScreenResult snapshotHit()
    {
        StockScreenResult hit = new StockScreenResult();
        hit.setTsCode("000001.SZ");
        hit.setName("平安银行");
        hit.setIndustry("银行");
        hit.setPeTtm(new BigDecimal("5.5"));
        return hit;
    }

    @Test
    void addRejectsBlankTsCode()
    {
        ServiceException ex = assertThrows(ServiceException.class, () -> service.add(2L, "  "));
        assertEquals("股票代码不能为空", ex.getMessage());
        verify(watchlistMapper, never()).insertWatchlist(any());
    }

    @Test
    void addRejectsWhenNoSuccessRun()
    {
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(null);
        ServiceException ex = assertThrows(ServiceException.class, () -> service.add(2L, "000001.SZ"));
        assertEquals("暂无成功的筛股快照，无法加入自选", ex.getMessage());
        verify(watchlistMapper, never()).insertWatchlist(any());
    }

    @Test
    void addRejectsWhenNotInLatestSnapshot()
    {
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(successRun());
        when(resultMapper.selectByRunIdAndTsCode(9L, "000001.SZ")).thenReturn(null);
        ServiceException ex = assertThrows(ServiceException.class, () -> service.add(2L, "000001.SZ"));
        assertEquals("该股票不在当前候选池中", ex.getMessage());
        verify(watchlistMapper, never()).insertWatchlist(any());
    }

    @Test
    void addRejectsDuplicate()
    {
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(successRun());
        when(resultMapper.selectByRunIdAndTsCode(9L, "000001.SZ")).thenReturn(snapshotHit());
        when(watchlistMapper.selectByUserIdAndTsCode(2L, "000001.SZ")).thenReturn(new StockWatchlist());
        ServiceException ex = assertThrows(ServiceException.class, () -> service.add(2L, "000001.SZ"));
        assertEquals("已在自选中", ex.getMessage());
        verify(watchlistMapper, never()).insertWatchlist(any());
    }

    @Test
    void addRejectsWhenAtCap()
    {
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(successRun());
        when(resultMapper.selectByRunIdAndTsCode(9L, "000001.SZ")).thenReturn(snapshotHit());
        when(watchlistMapper.selectByUserIdAndTsCode(2L, "000001.SZ")).thenReturn(null);
        when(watchlistMapper.countByUserId(2L)).thenReturn(200);
        ServiceException ex = assertThrows(ServiceException.class, () -> service.add(2L, "000001.SZ"));
        assertEquals("自选最多 200 只", ex.getMessage());
        verify(watchlistMapper, never()).insertWatchlist(any());
    }

    @Test
    void addInsertsNameCopiedFromSnapshot()
    {
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(successRun());
        when(resultMapper.selectByRunIdAndTsCode(9L, "000001.SZ")).thenReturn(snapshotHit());
        when(watchlistMapper.selectByUserIdAndTsCode(2L, "000001.SZ")).thenReturn(null);
        when(watchlistMapper.countByUserId(2L)).thenReturn(3);
        when(watchlistMapper.insertWatchlist(any(StockWatchlist.class))).thenReturn(1);

        service.add(2L, "000001.SZ");

        ArgumentCaptor<StockWatchlist> captor = ArgumentCaptor.forClass(StockWatchlist.class);
        verify(watchlistMapper).insertWatchlist(captor.capture());
        StockWatchlist saved = captor.getValue();
        assertEquals(Long.valueOf(2L), saved.getUserId());
        assertEquals("000001.SZ", saved.getTsCode());
        assertEquals("平安银行", saved.getName());
        assertEquals("银行", saved.getIndustry());
    }

    @Test
    void selectListJoinsLatestRunAndKeepsOutOfPoolRows()
    {
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(successRun());
        StockScreenResult gone = new StockScreenResult();
        gone.setTsCode("600000.SH");
        gone.setName("浦发银行");
        gone.setOutOfPool(Boolean.TRUE);
        when(watchlistMapper.selectWatchlistJoined(eq(2L), eq(9L), any(StockScreenResult.class)))
            .thenReturn(Collections.singletonList(gone));

        List<StockScreenResult> rows = service.selectList(2L, new StockScreenResult());

        assertEquals(1, rows.size());
        assertEquals("浦发银行", rows.get(0).getName());
        assertEquals(Boolean.TRUE, rows.get(0).getOutOfPool());
    }

    @Test
    void selectListPassesWholeQueryIncludingNumericMinToMapper()
    {
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(successRun());
        when(watchlistMapper.selectWatchlistJoined(eq(2L), eq(9L), any(StockScreenResult.class)))
            .thenReturn(Collections.emptyList());

        StockScreenResult query = new StockScreenResult();
        query.setRoeMin(new BigDecimal("8"));
        service.selectList(2L, query);

        ArgumentCaptor<StockScreenResult> captor = ArgumentCaptor.forClass(StockScreenResult.class);
        verify(watchlistMapper).selectWatchlistJoined(eq(2L), eq(9L), captor.capture());
        assertEquals(new BigDecimal("8"), captor.getValue().getRoeMin());
    }

    @Test
    void selectListClearsPageHelperBeforeResolvingLatestRun()
    {
        PageHelper.startPage(1, 20);
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(successRun());
        when(watchlistMapper.selectWatchlistJoined(eq(2L), eq(9L), any(StockScreenResult.class)))
            .thenReturn(Collections.emptyList());

        service.selectList(2L, new StockScreenResult());

        verify(runMapper).selectLatestSuccessRun("HIGH_DIVIDEND_MA120");
        assertEquals(1, PageHelper.getLocalPage().getPageNum());
        assertEquals(20, PageHelper.getLocalPage().getPageSize());
    }

    @Test
    void selectListAppliesWatchlistSortBeforeMapper()
    {
        StockScreenRun run = new StockScreenRun();
        run.setRunId(9L);
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(run);
        when(watchlistMapper.selectWatchlistJoined(eq(2L), eq(9L), any(StockScreenResult.class)))
            .thenReturn(Collections.emptyList());

        StockScreenResult query = new StockScreenResult();
        query.setSortBy("pb");
        query.setSortOrder("asc");
        service.selectList(2L, query);

        ArgumentCaptor<StockScreenResult> captor = ArgumentCaptor.forClass(StockScreenResult.class);
        verify(watchlistMapper).selectWatchlistJoined(eq(2L), eq(9L), captor.capture());
        assertEquals("r.pb is null, r.pb asc, w.ts_code asc", captor.getValue().getSafeOrderBy());
    }

    @Test
    void removeRejectsWhenNotOwned()
    {
        when(watchlistMapper.deleteByUserIdAndTsCode(2L, "000001.SZ")).thenReturn(0);
        ServiceException ex = assertThrows(ServiceException.class, () -> service.remove(2L, "000001.SZ"));
        assertEquals("该股票不在自选中", ex.getMessage());
    }

    @Test
    void removeDeletesOnlyCurrentUserRow()
    {
        when(watchlistMapper.deleteByUserIdAndTsCode(2L, "000001.SZ")).thenReturn(1);
        service.remove(2L, "000001.SZ");
        verify(watchlistMapper).deleteByUserIdAndTsCode(2L, "000001.SZ");
    }
}
