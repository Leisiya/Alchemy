-- 筛股定时任务：收盘后窗口每 30 分钟刷新（已有库可重复执行）
update sys_job
set cron_expression = '0 0/30 17-21 * * ?',
    remark = '每天 17:00–21:30 每 30 分钟刷新；非交易日或当天已成功则跳过',
    update_time = sysdate()
where invoke_target = 'stockScreeningTask.refreshLatest';
