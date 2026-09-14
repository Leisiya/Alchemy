-- ----------------------------
-- Alchemy 筛股缓存层：Tushare 原始数据缓存 + 同步水位
-- 字段对齐 Tushare 官方接口文档 https://tushare.pro/document/2
-- ----------------------------

-- 1、股票基础信息缓存（对应 stock_basic 接口）
drop table if exists stock_basic;
create table stock_basic (
  ts_code       varchar(16)   not null                   comment 'TS股票代码',
  symbol        varchar(16)   default ''                 comment '股票代码',
  name          varchar(64)   default ''                 comment '股票名称',
  area          varchar(32)   default ''                 comment '地域',
  industry      varchar(64)   default ''                 comment '所属行业',
  fullname      varchar(128)  default ''                 comment '股票全称',
  enname        varchar(128)  default ''                 comment '英文全称',
  cnspell       varchar(32)   default ''                 comment '拼音缩写',
  market        varchar(32)   default ''                 comment '市场类型',
  exchange      varchar(16)   default ''                 comment '交易所代码',
  curr_type     varchar(8)    default ''                 comment '交易货币',
  list_status   char(1)       default 'L'                comment '上市状态 L上市 D退市 P暂停上市',
  list_date     varchar(8)    default ''                 comment '上市日期',
  delist_date   varchar(8)    default ''                 comment '退市日期',
  is_hs         char(1)       default 'N'                comment '是否沪深港通标的 N否 H沪股通 S深股通',
  act_name      varchar(128)  default ''                 comment '实控人名称',
  act_ent_type  varchar(64)   default ''                 comment '实控人企业性质',
  update_time   datetime      default current_timestamp on update current_timestamp comment '本地更新时间',
  primary key (ts_code)
) engine=innodb comment = 'Tushare股票基础信息缓存';

-- 2、交易日历缓存（对应 trade_cal 接口）
drop table if exists stock_trade_cal;
create table stock_trade_cal (
  exchange       varchar(16)  not null                   comment '交易所',
  cal_date       varchar(8)   not null                   comment '日历日期',
  is_open        char(1)      default '0'                comment '是否交易 0休市 1交易',
  pretrade_date  varchar(8)   default ''                 comment '上一个交易日',
  primary key (exchange, cal_date),
  key idx_stock_trade_cal_is_open (exchange, is_open, cal_date)
) engine=innodb comment = 'Tushare交易日历缓存';

-- 3、每日估值指标缓存（对应 daily_basic 接口，存全字段）
drop table if exists stock_daily_basic;
create table stock_daily_basic (
  ts_code           varchar(16)     not null                comment 'TS股票代码',
  trade_date        varchar(8)      not null                comment '交易日期',
  close             decimal(18,4)   default null            comment '当日收盘价',
  turnover_rate     decimal(18,4)   default null            comment '换手率(%)',
  turnover_rate_f   decimal(18,4)   default null            comment '换手率(自由流通股)(%)',
  volume_ratio      decimal(18,4)   default null            comment '量比',
  pe                decimal(18,4)   default null            comment '市盈率',
  pe_ttm            decimal(18,4)   default null            comment '市盈率TTM',
  pb                decimal(18,4)   default null            comment '市净率',
  ps                decimal(18,4)   default null            comment '市销率',
  ps_ttm            decimal(18,4)   default null            comment '市销率TTM',
  dv_ratio          decimal(18,4)   default null            comment '股息率(%)',
  dv_ttm            decimal(18,4)   default null            comment '股息率TTM(%)',
  total_share       decimal(18,4)   default null            comment '总股本(万股)',
  float_share       decimal(18,4)   default null            comment '流通股本(万股)',
  free_share        decimal(18,4)   default null            comment '自由流通股本(万股)',
  total_mv          decimal(18,4)   default null            comment '总市值(万元)',
  circ_mv           decimal(18,4)   default null            comment '流通市值(万元)',
  limit_status      tinyint         default null            comment '收盘涨跌状态',
  primary key (ts_code, trade_date),
  key idx_stock_daily_basic_trade_date (trade_date)
) engine=innodb comment = 'Tushare每日指标缓存';

-- 4、日线行情缓存（对应 daily 接口，存全字段）
drop table if exists stock_daily_quote;
create table stock_daily_quote (
  ts_code       varchar(16)     not null                comment 'TS股票代码',
  trade_date    varchar(8)      not null                comment '交易日期',
  open          decimal(18,4)   default null            comment '开盘价',
  high          decimal(18,4)   default null            comment '最高价',
  low           decimal(18,4)   default null            comment '最低价',
  close         decimal(18,4)   default null            comment '收盘价',
  pre_close     decimal(18,4)   default null            comment '昨收价',
  `change`      decimal(18,4)   default null            comment '涨跌额',
  pct_chg       decimal(18,4)   default null            comment '涨跌幅(%)',
  vol           decimal(18,4)   default null            comment '成交量(手)',
  amount        decimal(18,4)   default null            comment '成交额(千元)',
  ah_vol        decimal(18,4)   default null            comment '盘后成交量(手)',
  ah_amount     decimal(18,4)   default null            comment '盘后成交额(千元)',
  primary key (ts_code, trade_date),
  key idx_stock_daily_quote_ts_code_trade_date (ts_code, trade_date desc)
) engine=innodb comment = 'Tushare日线行情缓存';

-- 5、财务指标缓存（对应 fina_indicator 接口）
drop table if exists stock_fina_indicator;
create table stock_fina_indicator (
  ts_code       varchar(16)     not null                comment 'TS股票代码',
  ann_date      varchar(8)      default ''              comment '公告日期',
  end_date      varchar(8)      not null                comment '报告期',
  roe           decimal(18,4)   default null            comment '净资产收益率(%)',
  update_flag   char(1)         default ''              comment '更新标识 0未修正 1修正',
  update_time   datetime        default current_timestamp on update current_timestamp comment '本地更新时间',
  primary key (ts_code, end_date)
) engine=innodb comment = 'Tushare财务指标缓存';

-- 6、分红送股缓存（对应 dividend 接口）
drop table if exists stock_dividend;
create table stock_dividend (
  ts_code         varchar(16)     not null                comment 'TS股票代码',
  end_date        varchar(8)      not null                comment '分红年度',
  ann_date        varchar(8)      not null                comment '预案公告日',
  div_proc        varchar(32)     not null                comment '实施进度',
  cash_div        decimal(18,4)   default null            comment '每股分红(税前)',
  cash_div_tax    decimal(18,4)   default null            comment '每股分红(税后)',
  ex_date         varchar(8)      default ''              comment '除权除息日',
  pay_date        varchar(8)      default ''              comment '派息日',
  update_time     datetime        default current_timestamp on update current_timestamp comment '本地更新时间',
  primary key (ts_code, end_date, ann_date, div_proc)
) engine=innodb comment = 'Tushare分红送股缓存';

-- 7、数据同步水位日志
drop table if exists stock_data_sync_log;
create table stock_data_sync_log (
  sync_id        bigint(20)      not null auto_increment  comment '同步记录ID',
  dataset        varchar(32)     not null                  comment '数据集：STOCK_BASIC/TRADE_CAL/DAILY_BASIC/DAILY_QUOTE',
  trade_date     varchar(8)      default ''                comment '本次同步锚定的交易日',
  row_count      int(11)         default 0                 comment '同步条数',
  status         char(1)         default '0'               comment '状态 0成功 1失败',
  error_message  varchar(1000)   default ''                comment '错误信息',
  started_at     datetime                                   comment '开始时间',
  finished_at    datetime                                   comment '结束时间',
  create_time    datetime                                   comment '创建时间',
  primary key (sync_id),
  unique key uk_stock_data_sync_log (dataset, trade_date, status),
  key idx_stock_data_sync_log_dataset_trade_date (dataset, trade_date)
) engine=innodb auto_increment=1 comment = '数据同步水位日志';

-- ----------------------------
-- 清空筛股测试快照（表结构保留，仅清测试数据）
-- stock_screen_result 有外键指向 stock_screen_run，需临时关闭外键检查才能 TRUNCATE 父表
-- ----------------------------
SET FOREIGN_KEY_CHECKS = 0;
truncate table stock_screen_result;
truncate table stock_screen_run;
SET FOREIGN_KEY_CHECKS = 1;
