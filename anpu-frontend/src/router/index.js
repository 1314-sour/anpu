import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login/index.vue'),
    hidden: true
  },
  {
    path: '/',
    component: () => import('@/views/Layout/index.vue'),
    redirect: '/login',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/Home/index.vue'),
        meta: { title: '首页', icon: 'dashboard' }
      },
      {
        path: 'user',
        component: () => import('@/views/UserCenter/index.vue'),
        redirect: '/user/security',
        children: [
          {
            path: 'security',
            name: 'SecuritySettings',
            component: () => import('@/views/UserCenter/Security.vue'),
            meta: { title: '安全设置' }
          },
          {
            path: 'profile',
            name: 'UserProfile',
            component: () => import('@/views/UserCenter/Profile.vue'),
            meta: { title: '基本资料' }
          },
          {
            path: 'system',
            name: 'SystemSettings',
            component: () => import('@/views/UserCenter/System.vue'),
            meta: { title: '系统设置' }
          },
          {
            path: 'logs',
            name: 'OperationLogs',
            component: () => import('@/views/UserCenter/Logs.vue'),
            meta: { title: '操作日志' }
          },
          {
            path: 'feedback',
            name: 'Feedback',
            component: () => import('@/views/UserCenter/Feedback.vue'),
            meta: { title: '意见反馈' }
          }
        ]
      },
      {
        path: 'message',
        component: () => import('@/views/MessageCenter/index.vue'),
        redirect: '/message/all',
        children: [
          {
            path: 'all',
            name: 'AllMessages',
            component: () => import('@/views/MessageCenter/AllMessages.vue'),
            meta: { title: '全部消息' }
          },
          {
            path: 'read',
            name: 'ReadMessages',
            component: () => import('@/views/MessageCenter/ReadMessages.vue'),
            meta: { title: '已读消息' }
          },
          {
            path: 'unread',
            name: 'UnreadMessages',
            component: () => import('@/views/MessageCenter/UnreadMessages.vue'),
            meta: { title: '未读消息' }
          }
        ]
      },
      {
        path: 'admin',
        component: () => import('@/views/Admin/index.vue'),
        redirect: '/admin/device-list',
        children: [
          {
            path: 'device-list',
            name: 'DeviceList',
            component: () => import('@/views/Admin/DeviceList.vue'),
            meta: { title: '设备管理', breadcrumb: ['设备中心', '设备管理'] }
          },
          {
            path: 'device-detail',
            name: 'DeviceDetail',
            component: () => import('@/views/Admin/DeviceDetail.vue'),
            meta: { title: '设备详情', breadcrumb: ['设备中心', '设备管理', '设备详情'] }
          },
          {
            path: 'group-list',
            name: 'GroupList',
            component: () => import('@/views/Admin/GroupList.vue'),
            meta: { title: '分组管理', breadcrumb: ['设备中心', '分组管理'] }
          },
          {
            path: 'device-access/safety',
            name: 'SafetyDeviceAccess',
            component: () => import('@/views/Admin/ProdEqui.vue'),
            meta: { title: '安全生产设备接入', breadcrumb: ['设备接入', '安全生产设备接入'] }
          },
          {
            path: 'device-access/monitor',
            name: 'MonitorDeviceAccess',
            component: () => import('@/views/Admin/MonitorEqui.vue'),
            meta: { title: '监控设备接入', breadcrumb: ['设备接入', '监控设备接入'] }
          },
          {
            path: 'device-access/firefight',
            name: 'FirefightDeviceAccess',
            component: () => import('@/views/Admin/FirefightEqui.vue'),
            meta: { title: '消防设备接入', breadcrumb: ['设备接入', '消防设备接入'] }
          },
          {
            path: 'device-access/other',
            name: 'OtherDeviceAccess',
            component: () => import('@/views/Admin/OtherEqui.vue'),
            meta: { title: '其他设备接入', breadcrumb: ['设备接入', '其他设备接入'] }
          },
          {
            path: 'data-summary',
            name: 'DataSummary',
            component: () => import('@/views/Admin/DataSummary.vue'),
            meta: { title: '数据中心', breadcrumb: ['数据汇总', '数据中心'] }
          },
          {
            path: 'api-interface',
            name: 'ApiInterface',
            component: () => import('@/views/Admin/ApiInterface.vue'),
            meta: { title: 'API接口', breadcrumb: ['API接口'] }
          },
          {
            path: 'data-mining',
            name: 'DataMining',
            component: () => import('@/views/Admin/DataMining.vue'),
            meta: { title: '数据挖掘与应用', breadcrumb: ['数据挖掘与应用'] }
          },
          {
            path: 'alarm-push',
            name: 'AlarmPush',
            component: () => import('@/views/Admin/AlarmPush.vue'),
            meta: { title: '报警信息推送', breadcrumb: ['报警信息推送'] }
          },
          {
            path: 'gm-center',
            name: 'GMCenter',
            component: () => import('@/views/Admin/GMCenter.vue'),
            meta: { title: 'GM管理', breadcrumb: ['GM中心', 'GM管理'] }
          },
          {
            path: 'internal-account',
            name: 'InternalAccountList',
            component: () => import('@/views/Admin/InternalAccountList.vue'),
            meta: { title: '内部账号管理', breadcrumb: ['账号管理', '内部账号管理'] }
          },
          {
            path: 'external-account',
            name: 'ExternalAccountList',
            component: () => import('@/views/Admin/ExternalAccountList.vue'),
            meta: { title: '外部企业账号管理', breadcrumb: ['账号管理', '外部企业账号管理'] }
          }
        ]
      }
    ]
  },
  // 404 page must be placed at the end !!!
  {
    path: '*',
    redirect: '/404',
    hidden: true
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// 简单的路由守卫（可选，暂时不做鉴权拦截，直接放行）
// router.beforeEach((to, from, next) => {
//   const hasToken = getToken()
//   if (hasToken) {
//     if (to.path === '/login') {
//       next({ path: '/' })
//     } else {
//       next()
//     }
//   } else {
//     if (whiteList.indexOf(to.path) !== -1) {
//       next()
//     } else {
//       next(`/login?redirect=${to.path}`)
//     }
//   }
// })

export default router
