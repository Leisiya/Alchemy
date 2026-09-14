package com.ruoyi.system.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * 股票筛选 CLI 作业配置（由若依 Quartz 通过 ProcessBuilder 触发）
 */
@Component
@ConfigurationProperties(prefix = "stock.screener")
public class StockScreenerProperties
{
    /** Python 可执行文件绝对路径，例如 venv/bin/python */
    private String pythonExecutable = "";

    /** stock-screening-service 工作目录 */
    private String workingDirectory = "";

    /** 模块名，默认 jobs.daily_run */
    private String jobModule = "jobs.daily_run";

    /** 进程超时秒数 */
    private int timeoutSeconds = 1800;

    public String getPythonExecutable()
    {
        return pythonExecutable;
    }

    public void setPythonExecutable(String pythonExecutable)
    {
        this.pythonExecutable = pythonExecutable;
    }

    public String getWorkingDirectory()
    {
        return workingDirectory;
    }

    public void setWorkingDirectory(String workingDirectory)
    {
        this.workingDirectory = workingDirectory;
    }

    public String getJobModule()
    {
        return jobModule;
    }

    public void setJobModule(String jobModule)
    {
        this.jobModule = jobModule;
    }

    public int getTimeoutSeconds()
    {
        return timeoutSeconds;
    }

    public void setTimeoutSeconds(int timeoutSeconds)
    {
        this.timeoutSeconds = timeoutSeconds;
    }
}
