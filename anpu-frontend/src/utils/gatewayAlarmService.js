import Vue from 'vue'

export const gatewayAlarmBus = new Vue()

let alarmWs = null
let heartbeatTimer = null
let reconnectTimer = null
let appStore = null

function refreshUnreadCount(delay = 0) {
  if (!appStore) {
    return
  }

  setTimeout(() => {
    appStore.dispatch('fetchUnreadCount')
  }, delay)
}

function canConnect(route) {
  const path = route && route.path
  return Boolean(localStorage.getItem('token')) && path !== '/login' && path !== '/'
}

function buildAlarmMessage(item) {
  const device = item.device_name || item.deviceName || '未知设备'
  const variable = item.variable_name || item.name || `变量ID ${item.id}`
  return `${device} 的 ${variable} 异常`
}

function prepareDesktopNotification() {
  if (!('Notification' in window) || Notification.permission !== 'default') {
    return
  }

  const permissionRequest = Notification.requestPermission()
  if (permissionRequest && typeof permissionRequest.catch === 'function') {
    permissionRequest.catch(() => {})
  }
}

function showAlarmNotification(item) {
  const title = '设备变量报警'
  const message = buildAlarmMessage(item)

  if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
    const notification = new Notification(title, {
      body: message,
      tag: `alarm:${item.gateway_no || 'gateway'}:${item.id}:${Date.now()}`,
      requireInteraction: true
    })
    notification.onclick = () => {
      window.focus()
      notification.close()
    }
    return
  }

  Vue.prototype.$notify({
    title,
    message,
    type: 'error',
    position: 'bottom-right',
    duration: 300000,
    showClose: true
  })
}

function handleGatewayMessage(msg) {
  if (!msg || msg.type === 'command_ack') {
    return
  }

  gatewayAlarmBus.$emit('gateway-realtime-message', msg)

  const variables = Array.isArray(msg.variables) ? msg.variables : []
  let hasAlarm = false

  variables.forEach(item => {
    const isAlarm = item.is_alarm !== undefined
      ? item.is_alarm
      : item.isAlarm !== undefined
        ? item.isAlarm
        : item.data_quality === 'alarm'

    if (isAlarm) {
      hasAlarm = true
      showAlarmNotification({
        ...item,
        gateway_no: msg.gateway_no
      })
    }
  })

  if (hasAlarm) {
    refreshUnreadCount()
    refreshUnreadCount(1000)
  }
}

export function stopGatewayAlarmService() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
  if (alarmWs) {
    alarmWs.onclose = null
    alarmWs.close()
    alarmWs = null
  }
}

export function startGatewayAlarmService(route) {
  if (!canConnect(route)) {
    stopGatewayAlarmService()
    return
  }

  prepareDesktopNotification()

  if (alarmWs && alarmWs.readyState !== WebSocket.CLOSED) {
    return
  }

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const wsUrl = `${protocol}://${window.location.host}/api/v1/gateway/ws`

  alarmWs = new WebSocket(wsUrl)

  alarmWs.onopen = () => {
    console.log('全局报警实时通道已连接')
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    heartbeatTimer = setInterval(() => {
      if (alarmWs && alarmWs.readyState === WebSocket.OPEN) {
        alarmWs.send('ping')
      }
    }, 30000)
  }

  alarmWs.onmessage = (event) => {
    try {
      handleGatewayMessage(JSON.parse(event.data))
    } catch (error) {
      console.error('解析全局网关实时数据失败:', error)
    }
  }

  alarmWs.onerror = (error) => {
    console.error('全局报警实时通道连接失败:', error)
  }

  alarmWs.onclose = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
    alarmWs = null
    reconnectTimer = setTimeout(() => {
      startGatewayAlarmService(route)
    }, 1000)
  }
}

export function setupGatewayAlarmService(router, store) {
  appStore = store

  router.afterEach((to) => {
    startGatewayAlarmService(to)
  })

  startGatewayAlarmService(router.currentRoute)
}
