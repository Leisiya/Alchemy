-- 分红送股缓存（对应 dividend 接口）
create table if not exists stock_dividend (
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
