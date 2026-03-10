import request from './request'

/**
 * 获取消息列表
 */
export function getMessages(params) {
  return request({
    url: '/v1/message/list',
    method: 'get',
    params
  })
}

/**
 * 获取未读消息数量
 */
export function getUnreadCount() {
  return request({
    url: '/v1/message/unread-count',
    method: 'get'
  })
}

/**
 * 标记消息为已读
 */
export function markRead(message_ids) {
  return request({
    url: '/v1/message/mark-read',
    method: 'post',
    data: message_ids
  })
}

/**
 * 全部标记为已读
 */
export function markAllRead(type) {
  return request({
    url: '/v1/message/mark-all-read',
    method: 'post',
    params: { type }
  })
}

/**
 * 标记消息为未读
 */
export function markUnread(message_ids) {
  return request({
    url: '/v1/message/mark-unread',
    method: 'post',
    data: message_ids
  })
}

/**
 * 删除消息
 */
export function deleteMessages(message_ids) {
  return request({
    url: '/v1/message/delete',
    method: 'delete',
    data: message_ids
  })
}
