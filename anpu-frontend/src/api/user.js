import request from './request'

/**
 * 获取用户资料
 */
export function getUserProfile() {
  return request({
    url: '/v1/user/profile',
    method: 'get'
  })
}

/**
 * 更新用户资料
 */
export function updateUserProfile(data) {
  return request({
    url: '/v1/user/profile',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 */
export function changePassword(data) {
  return request({
    url: '/v1/user/security/password',
    method: 'post',
    data
  })
}

/**
 * 更新头像
 */
export function updateAvatar(data) {
  return request({
    url: '/v1/user/security/avatar',
    method: 'post',
    data
  })
}

/**
 * 获取系统设置
 */
export function getUserSettings() {
  return request({
    url: '/v1/user/settings',
    method: 'get'
  })
}

/**
 * 更新系统设置
 */
export function updateUserSettings(data) {
  return request({
    url: '/v1/user/settings',
    method: 'put',
    data
  })
}

/**
 * 获取操作日志
 */
export function getOperationLogs(params) {
  return request({
    url: '/v1/user/logs',
    method: 'get',
    params
  })
}

/**
 * 提交反馈
 */
export function submitFeedback(data) {
  return request({
    url: '/v1/user/feedback',
    method: 'post',
    data
  })
}

/**
 * 获取反馈列表
 */
export function getFeedbacks(params) {
  return request({
    url: '/v1/user/feedback',
    method: 'get',
    params
  })
}
