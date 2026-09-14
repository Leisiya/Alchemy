import request from '@/utils/request'

export function listWatchlist(query) {
  return request({
    url: '/stock/watchlist/list',
    method: 'get',
    params: query
  })
}

export function listWatchlistCodes() {
  return request({
    url: '/stock/watchlist/codes',
    method: 'get'
  })
}

export function addWatchlist(tsCode) {
  return request({
    url: '/stock/watchlist',
    method: 'post',
    data: { tsCode }
  })
}

export function removeWatchlist(tsCode) {
  return request({
    url: '/stock/watchlist/' + tsCode,
    method: 'delete'
  })
}
