package com.ruoyi.system.domain.stock;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.ruoyi.common.annotation.Excel;
import org.junit.jupiter.api.Test;

class Ma120SignalDisplayTest
{
    @Test
    void blankSignalsExportAsPendingObservation()
    {
        assertEquals("有待观察", Ma120SignalDisplay.label(null));
        assertEquals("有待观察", Ma120SignalDisplay.label(""));
        assertEquals("有待观察", Ma120SignalDisplay.label("  "));
        assertEquals("有待观察", Ma120SignalDisplay.label("\t"));
    }

    @Test
    void knownSignalsStayUnchanged()
    {
        assertEquals("破位低估", Ma120SignalDisplay.label("破位低估"));
        assertEquals("强势突破", Ma120SignalDisplay.label("强势突破"));
    }

    @Test
    void excelHandlerFormatsBlankAsPendingObservation()
    {
        Ma120SignalDisplay handler = new Ma120SignalDisplay();
        assertEquals("有待观察", handler.format(null, new String[0], null, null));
        assertEquals("有待观察", handler.format("", new String[0], null, null));
        assertEquals("有待观察", handler.format(" ", new String[0], null, null));
        assertEquals("破位低估", handler.format("破位低估", new String[0], null, null));
        assertEquals("强势突破", handler.format("强势突破", new String[0], null, null));
    }

    @Test
    void screenResultSignalColumnUsesDisplayHandler() throws NoSuchFieldException
    {
        Excel excel = StockScreenResult.class.getDeclaredField("ma120Signal").getAnnotation(Excel.class);
        assertEquals("信号", excel.name());
        assertEquals(Ma120SignalDisplay.class, excel.handler());
    }
}
