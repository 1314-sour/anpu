import axios from 'axios'
import { Message } from 'element-ui'
// 统一的后端 API 地址，默认走 /api 交由 Nginx 反向代理
export const API_BASE_URL = '/api'

// 创建axios实例
const service = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000  // 增加到30秒
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    // 兼容后端两种成功响应格式：
    // 1. 统一包装格式：{ code: 200, message, data }
    // 2. 直接返回业务对象/数组
    if (res && typeof res === 'object' && !Object.prototype.hasOwnProperty.call(res, 'code')) {
      return res
    }
    if (res.code !== 200) {
      Message({ message: res.message || '请求失败', type: 'error', duration: 3000 })
      if (res.code === 401 && !response.config.url.includes('/auth/login')) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        setTimeout(() => { window.location.href = '/login' }, 1500)
      }
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  error => {
    let message = '网络错误'
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        message = '登录已过期,请重新登录'
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        setTimeout(() => { window.location.href = '/login' }, 1500)
      } else if (status === 403) {
        message = '没有权限访问'
      } else if (status === 404) {
        message = '请求的资源不存在'
      } else if (status === 500) {
        message = '服务器错误'
      } else if (data && data.message) {
        message = data.message
      }
    } else if (error.request) {
      if (error.code === 'ECONNABORTED') {
        message = '请求超时,请检查网络'
      } else if (error.message.includes('Network Error')) {
        message = `网络连接失败,请检查后端服务是否启动(${API_BASE_URL})`
      } else {
        message = '网络错误,请稍后重试'
      }
    } else {
      message = error.message || '未知错误'
    }
    Message({ message, type: 'error', duration: 5000 })
    return Promise.reject(error)
  }
)

export default service
