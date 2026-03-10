import request from './request'

/**
 * 设备管理 API
 */

// 获取设备详情
export function getDeviceDetail(id) {
  return request({
    url: `/v1/device/detail/${id}`,
    method: 'get'
  })
}

// 获取设备列表
export function getDevices(params) {
  return request({
    url: '/v1/device/list',
    method: 'get',
    params
  })
}

// 创建设备
export function createDevice(data) {
  return request({
    url: '/v1/device/create',
    method: 'post',
    data
  })
}

// 更新设备
export function updateDevice(id, data) {
  return request({
    url: `/v1/device/update/${id}`,
    method: 'put',
    data
  })
}

// 删除设备
export function deleteDevice(id) {
  return request({
    url: `/v1/device/delete/${id}`,
    method: 'delete'
  })
}

// 批量更新设备分组
export function batchUpdateGroup(device_ids, group_id) {
  return request({
    url: '/v1/device/batch-update-group',
    method: 'post',
    data: { device_ids, group_id }
  })
}

/**
 * 分组管理 API
 */

// 获取分组列表
export function getGroups() {
  return request({
    url: '/v1/device/groups/list',
    method: 'get'
  })
}

// 创建分组
export function createGroup(data) {
  return request({
    url: '/v1/device/groups/create',
    method: 'post',
    data
  })
}

// 更新分组
export function updateGroup(id, data) {
  return request({
    url: `/v1/device/groups/update/${id}`,
    method: 'put',
    data
  })
}

// 删除分组
export function deleteGroup(id) {
  return request({
    url: `/v1/device/groups/delete/${id}`,
    method: 'delete'
  })
}

// 获取分组下的设备
export function getGroupDevices(groupId, params) {
  return request({
    url: `/v1/device/groups/${groupId}/devices`,
    method: 'get',
    params
  })
}

// 从分组移除设备
export function removeDevicesFromGroup(groupId, device_ids) {
  return request({
    url: `/v1/device/groups/${groupId}/remove-devices`,
    method: 'post',
    data: device_ids
  })
}

// 检查设备名称是否已存在
export function checkDeviceName(name, excludeId = null) {
  return request({
    url: '/v1/device/check-name',
    method: 'get',
    params: { 
      name,
      exclude_id: excludeId
    }
  })
}
