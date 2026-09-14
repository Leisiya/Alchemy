-- ROE 财务指标缓存 + 筛股结果 roe 列（已有库可重复执行；不要重跑整份 ry_20260417.sql）

create table if not exists stock_fina_indicator (
  ts_code       varchar(16)     not null                comment 'TS股票代码',
  ann_date      varchar(8)      default ''              comment '公告日期',
  end_date      varchar(8)      not null                comment '报告期',
  roe           decimal(18,4)   default null            comment '净资产收益率(%)',
  update_flag   char(1)         default ''              comment '更新标识 0未修正 1修正',
  update_time   datetime        default current_timestamp on update current_timestamp comment '本地更新时间',
  primary key (ts_code, end_date)
) engine=innodb comment = 'Tushare财务指标缓存';

set @db_name = database();
set @column_exists = (
  select count(*)
  from information_schema.columns
  where table_schema = @db_name
    and table_name = 'stock_screen_result'
    and column_name = 'roe'
);
set @sql = if(
  @column_exists = 0,
  'alter table stock_screen_result add column roe decimal(18,4) default null comment ''ROE'' after pb',
  'select 1'
);
prepare stmt from @sql;
execute stmt;
deallocate prepare stmt;
