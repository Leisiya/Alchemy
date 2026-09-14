import request from '@/utils/request'

export function listInbox() {
  return request({
    url: '/system/notice/inbox',
    method: 'get'
  })
}

export function getNoticeUnreadCount() {
  return request({
    url: '/system/notice/unread-count',
    method: 'get'
  })
}

export function markNoticeRead(noticeId) {
  return request({
    url: '/system/notice/read/' + noticeId,
    method: 'put'
  })
}

export function markNoticeReadAll() {
  return request({
    url: '/system/notice/read-all',
    method: 'put'
  })
}

export function listNotice(query) {
  return request({
    url: '/system/notice/list',
    method: 'get',
    params: query
  })
}

export function getNotice(noticeId) {
  return request({
    url: '/system/notice/' + noticeId,
    method: 'get'
  })
}

export function addNotice(data) {
  return request({
    url: '/system/notice',
    method: 'post',
    data: data
  })
}

export function updateNotice(data) {
  return request({
    url: '/system/notice',
    method: 'put',
    data: data
  })
}

export function delNotice(noticeId) {
  return request({
    url: '/system/notice/' + noticeId,
    method: 'delete'
  })
}
