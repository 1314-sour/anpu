import request from './request'

// ========== 设备详细配置 ==========
export function getDeviceConfig(deviceId) {
  return request({
    url: `/v1/device-detail/${deviceId}/config`,
    method: 'get'
  })
}

export function createDeviceConfig(deviceId, data) {
  return request({
    url: `/v1/device-detail/${deviceId}/config`,
    method: 'post',
    data
  })
}

export function updateDeviceConfig(deviceId, data) {
  return request({
    url: `/v1/device-detail/${deviceId}/config`,
    method: 'put',
    data
  })
}

// ========== 网关驱动管理 ==========
export function getDeviceDrivers(deviceId) {
  return request({
    url: `/v1/device-detail/${deviceId}/drivers`,
    method: 'get'
  })
}

export function createDeviceDriver(deviceId, data) {
  return request({
    url: `/v1/device-detail/${deviceId}/drivers`,
    method: 'post',
    data
  })
}

export function updateDeviceDriver(deviceId, driverId, data) {
  return request({
    url: `/v1/device-detail/${deviceId}/drivers/${driverId}`,
    method: 'put',
    data
  })
}

export function deleteDeviceDriver(deviceId, driverId) {
  return request({
    url: `/v1/device-detail/${deviceId}/drivers/${driverId}`,
    method: 'delete'
  })
}

// ========== 设备变量管理 ==========
export function getDeviceVariables(deviceId, params) {
  return request({
    url: `/v1/device-detail/${deviceId}/variables`,
    method: 'get',
    params
  })
}

export function createDeviceVariable(deviceId, data) {
  return request({
    url: `/v1/device-detail/${deviceId}/variables`,
    method: 'post',
    data
  })
}

export function batchCreateVariables(deviceId, variables) {
  return request({
    url: `/v1/device-detail/${deviceId}/variables/batch`,
    method: 'post',
    data: { variables }
  })
}

export function updateDeviceVariable(deviceId, variableId, data) {
  return request({
    url: `/v1/device-detail/${deviceId}/variables/${variableId}`,
    method: 'put',
    data
  })
}

export function batchDeleteVariables(deviceId, ids) {
  return request({
    url: `/v1/device-detail/${deviceId}/variables`,
    method: 'delete',
    data: { ids }
  })
}

// ========== 历史报表管理 ==========
export function getDeviceReports(deviceId) {
  return request({
    url: `/v1/device-detail/${deviceId}/reports`,
    method: 'get'
  })
}

export function createDeviceReport(deviceId, data) {
  return request({
    url: `/v1/device-detail/${deviceId}/reports`,
    method: 'post',
    data
  })
}

export function updateDeviceReport(deviceId, reportId, data) {
  return request({
    url: `/v1/device-detail/${deviceId}/reports/${reportId}`,
    method: 'put',
    data
  })
}

export function deleteDeviceReport(deviceId, reportId) {
  return request({
    url: `/v1/device-detail/${deviceId}/reports/${reportId}`,
    method: 'delete'
  })
}

// ========== 报告管理 ==========
export function getDeviceAlarms(deviceId) {
  return request({
    url: `/v1/device-detail/${deviceId}/alarms`,
    method: 'get'
  })
}

export function createDeviceAlarm(deviceId, data) {
  return request({
    url: `/v1/device-detail/${deviceId}/alarms`,
    method: 'post',
    data
  })
}

export function updateDeviceAlarm(deviceId, alarmId, data) {
  return request({
    url: `/v1/device-detail/${deviceId}/alarms/${alarmId}`,
    method: 'put',
    data
  })
}

export function deleteDeviceAlarm(deviceId, alarmId) {
  return request({
    url: `/v1/device-detail/${deviceId}/alarms/${alarmId}`,
    method: 'delete'
  })
}
