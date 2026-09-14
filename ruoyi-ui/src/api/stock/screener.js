import request from '@/utils/request'

// 查询筛股结果列表
export function listScreenResults(query) {
  return request({
    url: '/stock/screener/results/list',
    method: 'get',
    params: query
  })
}

// 获取最新成功运行摘要
export function getLatestScreenRun() {
  return request({
    url: '/stock/screener/runs/latest',
    method: 'get'
  })
}

// 获取可选交易日
export function getScreenRunOptions() {
  return request({
    url: '/stock/screener/runs/options',
    method: 'get'
  })
}

// 获取仪表页数据
export function getLatestScreenDashboard() {
  return request({
    url: '/stock/screener/dashboard/latest',
    method: 'get'
  })
}
