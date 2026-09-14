-- 用户自选股表（已有库可重复执行；不要重跑整份 ry_20260417.sql）
create table if not exists stock_watchlist (
  watchlist_id      bigint(20)      not null auto_increment    comment '自选ID',
  user_id           bigint(20)      not null                   comment '用户ID',
  ts_code           varchar(16)     not null                   comment '股票代码',
  name              varchar(64)     default ''                 comment '加入时股票名称',
  industry          varchar(128)    default ''                 comment '加入时行业',
  create_time       datetime                                   comment '创建时间',
  primary key (watchlist_id),
  unique key uk_stock_watchlist_user_ts (user_id, ts_code),
  key idx_stock_watchlist_user_time (user_id, create_time)
) engine=innodb auto_increment=1 comment = '用户自选股表';
