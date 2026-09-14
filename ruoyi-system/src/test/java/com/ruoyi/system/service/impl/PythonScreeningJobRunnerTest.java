package com.ruoyi.system.service.impl;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.util.concurrent.TimeUnit;

import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.system.config.StockScreenerProperties;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class PythonScreeningJobRunnerTest
{
    private StockScreenerProperties props;

    @BeforeEach
    void setUp()
    {
        props = new StockScreenerProperties();
        props.setPythonExecutable("/usr/bin/python3");
        props.setWorkingDirectory("/tmp/svc");
        props.setJobModule("jobs.daily_run");
        props.setTimeoutSeconds(30);
    }

    @Test
    void runSucceedsOnExitCodeZero() throws Exception
    {
        Process process = mock(Process.class);
        when(process.waitFor(30L, TimeUnit.SECONDS)).thenReturn(true);
        when(process.exitValue()).thenReturn(0);

        PythonScreeningJobRunner runner = new PythonScreeningJobRunner(props, command -> process);
        assertDoesNotThrow(() -> runner.run(null));
    }

    @Test
    void runThrowsOnNonZeroExit() throws Exception
    {
        Process process = mock(Process.class);
        when(process.waitFor(30L, TimeUnit.SECONDS)).thenReturn(true);
        when(process.exitValue()).thenReturn(1);

        PythonScreeningJobRunner runner = new PythonScreeningJobRunner(props, command -> process);
        assertThrows(ServiceException.class, () -> runner.run("20260722"));
    }

    @Test
    void runThrowsOnTimeout() throws Exception
    {
        Process process = mock(Process.class);
        when(process.waitFor(30L, TimeUnit.SECONDS)).thenReturn(false);

        PythonScreeningJobRunner runner = new PythonScreeningJobRunner(props, command -> process);
        assertThrows(ServiceException.class, () -> runner.run(null));
    }
}
