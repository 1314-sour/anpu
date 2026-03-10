<template>
  <div class="admin-container">
    <el-container class="content-box">
      <!-- 左侧深色侧边栏 -->
      <el-aside width="220px" class="sidebar">
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu"
          router
          background-color="#303133"
          text-color="#fff"
          active-text-color="#409EFF"
          :unique-opened="false">
          
          <el-submenu index="device-center">
            <template slot="title">
              <i class="el-icon-monitor"></i>
              <span>设备中心</span>
            </template>
            <el-menu-item index="/admin/device-list">设备管理</el-menu-item>
            <el-menu-item index="/admin/group-list">分组管理</el-menu-item>
          </el-submenu>

          <el-submenu index="device-access">
            <template slot="title">
              <i class="el-icon-connection"></i>
              <span>设备接入</span>
            </template>
            <el-menu-item index="/admin/device-access/safety">安全生产设备接入</el-menu-item>
            <el-menu-item index="/admin/device-access/monitor">监控设备接入</el-menu-item>
            <el-menu-item index="/admin/device-access/firefight">消防设备接入</el-menu-item>
            <el-menu-item index="/admin/device-access/other">其他设备接入</el-menu-item>
          </el-submenu>

          <el-submenu index="data-summary">
            <template slot="title">
              <i class="el-icon-s-data"></i>
              <span>数据汇总</span>
            </template>
            <el-menu-item index="/admin/data-summary">数据中心</el-menu-item>
          </el-submenu>
          
          <el-menu-item index="/admin/api-interface">
            <i class="el-icon-link"></i>
            <span slot="title">API接口</span>
          </el-menu-item>

          <el-menu-item index="/admin/data-mining">
            <i class="el-icon-coin"></i>
            <span slot="title">数据挖掘与应用</span>
          </el-menu-item>

          <el-menu-item index="/admin/alarm-push">
            <i class="el-icon-bell"></i>
            <span slot="title">报警信息推送</span>
          </el-menu-item>

          <el-submenu index="gm-center">
            <template slot="title">
              <i class="el-icon-s-grid"></i>
              <span>GM中心</span>
            </template>
            <el-menu-item index="/admin/gm-center">GM管理</el-menu-item>
          </el-submenu>

          <el-submenu index="account-management">
            <template slot="title">
              <i class="el-icon-user-solid"></i>
              <span>账号管理</span>
            </template>
            <el-menu-item index="/admin/internal-account">内部账号管理</el-menu-item>
            <el-menu-item index="/admin/external-account">外部企业账号管理</el-menu-item>
          </el-submenu>
        </el-menu>
      </el-aside>

      <!-- 右侧内容区 -->
      <el-main class="main-content">
        <div class="breadcrumb-container">
           <el-breadcrumb separator="/">
            <el-breadcrumb-item>后台管理</el-breadcrumb-item>
            <el-breadcrumb-item 
              v-for="(item, index) in $route.meta.breadcrumb" 
              :key="index"
              :to="getBreadcrumbPath(item, index)">
              {{ item }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'AdminLayout',
  methods: {
    getBreadcrumbPath(item, index) {
      // 根据面包屑文字返回对应的路由路径
      const breadcrumbMap = {
        '设备中心': null,  // 一级菜单不跳转
        '设备管理': '/admin/device-list',
        '分组管理': '/admin/group-list',
        '设备接入': null,
        '安全生产设备接入': '/admin/device-access/safety',
        '监控设备接入': '/admin/device-access/monitor',
        '消防设备接入': '/admin/device-access/firefight',
        '其他设备接入': '/admin/device-access/other',
        '数据汇总': null,
        '数据中心': '/admin/data-summary',
        'API接口': '/admin/api-interface',
        '数据挖掘与应用': '/admin/data-mining',
        '报警信息推送': '/admin/alarm-push',
        'GM中心': null,
        'GM管理': '/admin/gm-center',
        '账号管理': null,
        '内部账号管理': '/admin/internal-account',
        '外部企业账号管理': '/admin/external-account',
        '设备详情': null  // 详情页不需要跳转
      }
      
      // 如果是最后一个面包屑或者没有对应路径，不设置跳转
      const isLast = index === this.$route.meta.breadcrumb.length - 1
      return isLast ? null : breadcrumbMap[item]
    }
  }
}
</script>

<style scoped>
.admin-container {
  height: calc(100vh - 60px); /* 减去顶部导航栏高度 */
  background-color: #f0f2f5;
  box-sizing: border-box;
}

.content-box {
  height: 100%;
}

.sidebar {
  background-color: #303133;
  height: 100%;
  overflow-x: hidden;
}

.sidebar-menu {
  border-right: none;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
  background-color: #fff;
  margin: 10px;
  border-radius: 4px;
}

.breadcrumb-container {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}
</style>
