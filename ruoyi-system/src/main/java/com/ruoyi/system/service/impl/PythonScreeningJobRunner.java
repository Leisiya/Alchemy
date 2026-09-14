package com.ruoyi.system.service.impl;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.system.config.StockScreenerProperties;

/**
 * 通过 ProcessBuilder 运行 Python 筛股 CLI
 */
@Component
public class PythonScreeningJobRunner
{
    private static final Logger log = LoggerFactory.getLogger(PythonScreeningJobRunner.class);

    @FunctionalInterface
    public interface ProcessFactory
    {
        Process start(List<String> command) throws IOException;
    }

    private final StockScreenerProperties properties;

    private final ProcessFactory processFactory;

    @Autowired
    public PythonScreeningJobRunner(StockScreenerProperties properties)
    {
        this.properties = properties;
        this.processFactory = this::startWithDirectory;
    }

    PythonScreeningJobRunner(StockScreenerProperties properties, ProcessFactory processFactory)
    {
        this.properties = properties;
        this.processFactory = processFactory;
    }

    public void run(String tradeDate)
    {
        validateConfig();
        List<String> command = buildCommand(tradeDate);
        log.info("Starting screening CLI: {}", command);
        Process process = null;
        try
        {
            process = processFactory.start(command);
            boolean finished = process.waitFor(properties.getTimeoutSeconds(), TimeUnit.SECONDS);
            if (!finished)
            {
                process.destroyForcibly();
                throw new ServiceException("股票筛选 CLI 超时（" + properties.getTimeoutSeconds() + "s）");
            }
            int exit = process.exitValue();
            if (exit != 0)
            {
                throw new ServiceException("股票筛选 CLI 失败，exitCode=" + exit);
            }
        }
        catch (ServiceException ex)
        {
            throw ex;
        }
        catch (Exception ex)
        {
            throw new ServiceException("启动股票筛选 CLI 失败：" + ex.getMessage());
        }
        finally
        {
            if (process != null && process.isAlive())
            {
                process.destroyForcibly();
            }
        }
    }

    List<String> buildCommand(String tradeDate)
    {
        List<String> command = new ArrayList<String>();
        command.add(properties.getPythonExecutable());
        command.add("-m");
        command.add(properties.getJobModule());
        if (StringUtils.isNotEmpty(tradeDate))
        {
            command.add("--trade-date");
            command.add(tradeDate);
        }
        return command;
    }

    private void validateConfig()
    {
        if (StringUtils.isEmpty(properties.getPythonExecutable()))
        {
            throw new ServiceException("未配置 stock.screener.python-executable");
        }
        if (StringUtils.isEmpty(properties.getWorkingDirectory()))
        {
            throw new ServiceException("未配置 stock.screener.working-directory");
        }
        if (StringUtils.isEmpty(properties.getJobModule()))
        {
            throw new ServiceException("未配置 stock.screener.job-module");
        }
    }

    private Process startWithDirectory(List<String> command) throws IOException
    {
        ProcessBuilder builder = new ProcessBuilder(command);
        builder.directory(new File(properties.getWorkingDirectory()));
        builder.redirectErrorStream(true);
        builder.inheritIO();
        return builder.start();
    }
}
