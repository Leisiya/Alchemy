package com.ruoyi.system.service.impl;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import com.github.pagehelper.Page;
import com.github.pagehelper.PageHelper;
import com.ruoyi.system.domain.stock.StockScreenResult;
import com.ruoyi.system.domain.stock.StockScreenRun;
import com.ruoyi.system.mapper.stock.StockScreenResultMapper;
import com.ruoyi.system.mapper.stock.StockScreenRunMapper;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class StockScreeningServiceImplTest
{
    @Mock
    private StockScreenRunMapper runMapper;

    @Mock
    private StockScreenResultMapper resultMapper;

    @Mock
    private PythonScreeningJobRunner pythonScreeningJobRunner;

    @InjectMocks
    private StockScreeningServiceImpl service;

    @AfterEach
    void clearPageHelper()
    {
        PageHelper.clearPage();
    }

    @Test
    void refreshLatestDelegatesToPythonJobRunner()
    {
        service.refreshLatest();

        verify(pythonScreeningJobRunner, times(1)).run(isNull());
        verifyNoInteractions(runMapper);
        verifyNoInteractions(resultMapper);
    }

    @Test
    void selectResultListWithoutSignalUsesLatestTradeDateAndKeepsSignalEmpty()
    {
        StockScreenRun run = new StockScreenRun();
        run.setTradeDate("20260813");
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(run);
        when(resultMapper.selectResultList(any(StockScreenResult.class))).thenReturn(Collections.emptyList());

        StockScreenResult query = new StockScreenResult();
        List<StockScreenResult> rows = service.selectResultList(query);

        ArgumentCaptor<StockScreenResult> captor = ArgumentCaptor.forClass(StockScreenResult.class);
        verify(resultMapper).selectResultList(captor.capture());
        StockScreenResult sent = captor.getValue();
        assertEquals("20260813", sent.getTradeDate());
        assertEquals("HIGH_DIVIDEND_MA120", sent.getStrategyCode());
        assertTrue(sent.getSignal() == null || sent.getSignal().isEmpty());
        assertEquals(0, rows.size());
    }

    @Test
    void selectResultListForwardsBreakoutSignal()
    {
        StockScreenRun run = new StockScreenRun();
        run.setTradeDate("20260813");
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(run);
        StockScreenResult hit = new StockScreenResult();
        hit.setTsCode("601886.SH");
        hit.setMa120Signal("强势突破");
        when(resultMapper.selectResultList(any(StockScreenResult.class))).thenReturn(Collections.singletonList(hit));

        StockScreenResult query = new StockScreenResult();
        query.setSignal("强势突破");
        List<StockScreenResult> rows = service.selectResultList(query);

        ArgumentCaptor<StockScreenResult> captor = ArgumentCaptor.forClass(StockScreenResult.class);
        verify(resultMapper).selectResultList(captor.capture());
        assertEquals("强势突破", captor.getValue().getSignal());
        assertEquals(1, rows.size());
        assertEquals("强势突破", rows.get(0).getMa120Signal());
    }

    @Test
    void selectResultListForwardsUndervaluedSignal()
    {
        StockScreenRun run = new StockScreenRun();
        run.setTradeDate("20260813");
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(run);
        when(resultMapper.selectResultList(any(StockScreenResult.class))).thenReturn(Collections.emptyList());

        StockScreenResult query = new StockScreenResult();
        query.setSignal("破位低估");
        service.selectResultList(query);

        ArgumentCaptor<StockScreenResult> captor = ArgumentCaptor.forClass(StockScreenResult.class);
        verify(resultMapper).selectResultList(captor.capture());
        assertEquals("破位低估", captor.getValue().getSignal());
    }

    @Test
    void selectResultListForwardsNumericMinMaxToMapper()
    {
        StockScreenRun run = new StockScreenRun();
        run.setTradeDate("20260813");
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(run);
        when(resultMapper.selectResultList(any(StockScreenResult.class))).thenReturn(Collections.emptyList());

        StockScreenResult query = new StockScreenResult();
        query.setPeTtmMin(new BigDecimal("5"));
        query.setPeTtmMax(new BigDecimal("20"));
        service.selectResultList(query);

        ArgumentCaptor<StockScreenResult> captor = ArgumentCaptor.forClass(StockScreenResult.class);
        verify(resultMapper).selectResultList(captor.capture());
        assertEquals(new BigDecimal("5"), captor.getValue().getPeTtmMin());
        assertEquals(new BigDecimal("20"), captor.getValue().getPeTtmMax());
    }

    @Test
    void selectResultListRestoresPageHelperAfterResolvingTradeDate()
    {
        PageHelper.startPage(2, 10);
        StockScreenRun run = new StockScreenRun();
        run.setTradeDate("20260813");
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(run);
        when(resultMapper.selectResultList(any(StockScreenResult.class))).thenReturn(Collections.emptyList());

        service.selectResultList(new StockScreenResult());

        Page<?> page = PageHelper.getLocalPage();
        assertNotNull(page);
        assertEquals(2, page.getPageNum());
        assertEquals(10, page.getPageSize());
    }

    @Test
    void selectLatestDashboardClearsPageHelperBeforeLatestRunQuery()
    {
        PageHelper.startPage(1, 20);
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenAnswer(invocation -> {
            assertNull(PageHelper.getLocalPage());
            return null;
        });

        service.selectLatestDashboard();

        verify(runMapper).selectLatestSuccessRun("HIGH_DIVIDEND_MA120");
    }

    @Test
    void selectResultListClearsPageHelperWhenLatestRunIsNull()
    {
        PageHelper.startPage(1, 20);
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(null);

        List<StockScreenResult> rows = service.selectResultList(new StockScreenResult());

        assertEquals(0, rows.size());
        assertNull(PageHelper.getLocalPage());
    }

    @Test
    void selectResultListAppliesWhitelistedSortBeforeMapper()
    {
        StockScreenRun run = new StockScreenRun();
        run.setTradeDate("20260813");
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(run);
        when(resultMapper.selectResultList(any(StockScreenResult.class))).thenReturn(Collections.emptyList());

        StockScreenResult query = new StockScreenResult();
        query.setSortBy("peTtm");
        query.setSortOrder("asc");
        service.selectResultList(query);

        ArgumentCaptor<StockScreenResult> captor = ArgumentCaptor.forClass(StockScreenResult.class);
        verify(resultMapper).selectResultList(captor.capture());
        assertEquals("pe_ttm is null, pe_ttm asc, ts_code asc", captor.getValue().getSafeOrderBy());
        assertEquals("20260813", captor.getValue().getTradeDate());
    }

    @Test
    void selectResultListAppliesPageDefaultWhenSortIsAbsent()
    {
        StockScreenRun run = new StockScreenRun();
        run.setTradeDate("20260813");
        when(runMapper.selectLatestSuccessRun("HIGH_DIVIDEND_MA120")).thenReturn(run);
        when(resultMapper.selectResultList(any(StockScreenResult.class))).thenReturn(Collections.emptyList());

        StockScreenResult query = new StockScreenResult();
        query.setSignal("破位低估");
        service.selectResultList(query);

        ArgumentCaptor<StockScreenResult> captor = ArgumentCaptor.forClass(StockScreenResult.class);
        verify(resultMapper).selectResultList(captor.capture());
        assertEquals("price_ma120_ratio asc, dv_ttm desc, ts_code asc", captor.getValue().getSafeOrderBy());
    }
}
