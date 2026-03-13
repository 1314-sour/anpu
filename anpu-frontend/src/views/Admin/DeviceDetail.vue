<template>
  <div class="device-detail-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" style="margin-bottom: 20px;">
      <el-breadcrumb-item :to="{ path: '/admin/device' }">设备管理</el-breadcrumb-item>
      <el-breadcrumb-item>{{ mode === 'create' ? '新增设备' : '编辑设备' }}</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- Tab页签 -->
    <el-tabs v-model="currentTab" @tab-click="handleTabClick">
      <el-tab-pane label="设备基本信息" name="basic" :disabled="isTabDisabled('basic')">
        <BasicInfo 
          :device-id="deviceId" 
          :mode="mode" 
          @next="handleNext" 
          @device-created="handleDeviceCreated"
        />
      </el-tab-pane>
      
      <el-tab-pane label="网关、驱动管理" name="drivers" :disabled="isTabDisabled('drivers')">
        <DriversManage 
          v-if="deviceId" 
          :device-id="deviceId" 
          :mode="mode" 
          @next="handleNext"
        />
      </el-tab-pane>
      
      <el-tab-pane label="变量管理" name="variables" :disabled="isTabDisabled('variables')">
        <VariablesManage 
          v-if="deviceId" 
          :device-id="deviceId" 
          :mode="mode" 
          :gateway-sn="gatewaySn"
          @next="handleNext"
        />
      </el-tab-pane>
      
      <el-tab-pane label="历史报表管理" name="reports" :disabled="isTabDisabled('reports')">
        <ReportsManage 
          v-if="deviceId" 
          :device-id="deviceId" 
          :mode="mode" 
          @next="handleNext"
        />
      </el-tab-pane>
      
      <el-tab-pane label="报告管理" name="alarms" :disabled="isTabDisabled('alarms')">
        <AlarmsManage 
          v-if="deviceId" 
          :device-id="deviceId" 
          :mode="mode"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import BasicInfo from './DeviceDetail/BasicInfo.vue'
import DriversManage from './DeviceDetail/DriversManage.vue'
import VariablesManage from './DeviceDetail/VariablesManage.vue'
import ReportsManage from './DeviceDetail/ReportsManage.vue'
import AlarmsManage from './DeviceDetail/AlarmsManage.vue'

export default {
  name: 'DeviceDetail',
  components: {
    BasicInfo,
    DriversManage,
    VariablesManage,
    ReportsManage,
    AlarmsManage
  },
  data() {
    return {
      mode: 'edit', // 'edit' 或 'create'
      deviceId: null,
      gatewaySn: '',
      currentTab: 'basic',
      completedTabs: [], // 新增模式下已完成的Tab
      tabs: ['basic', 'drivers', 'variables', 'reports', 'alarms']
    }
  },
  created() {
    const { id, mode, sn } = this.$route.query
    this.mode = mode || 'edit'
    this.deviceId = id ? parseInt(id) : null
    this.gatewaySn = sn || ''
    
    if (this.mode === 'edit' && !this.deviceId) {
      this.$message.error('缺少设备ID')
      this.$router.back()
    }
  },
  methods: {
    // 检查Tab是否禁用
    isTabDisabled(tabName) {
      if (this.mode === 'edit') return false // 编辑模式全部可点击
      
      // 新增模式：必须有deviceId才能进入后续Tab
      if (tabName !== 'basic' && !this.deviceId) return true
      
      // 必须按顺序完成
      const tabIndex = this.tabs.indexOf(tabName)
      const completedIndex = this.tabs.indexOf(this.completedTabs[this.completedTabs.length - 1] || 'basic')
      
      return tabIndex > completedIndex + 1
    },
    
    // Tab点击事件
    handleTabClick(tab) {
      if (!this.deviceId && tab.name !== 'basic') {
        this.$message.warning('请先完成设备基本信息填写')
        this.currentTab = 'basic'
      }
    },
    
    // 进入下一个Tab
    handleNext() {
      // 标记当前Tab完成
      if (!this.completedTabs.includes(this.currentTab)) {
        this.completedTabs.push(this.currentTab)
      }
      
      // 进入下一个Tab
      const currentIndex = this.tabs.indexOf(this.currentTab)
      if (currentIndex < this.tabs.length - 1) {
        this.currentTab = this.tabs[currentIndex + 1]
      } else {
        // 全部完成，返回列表
        this.$message.success('设备配置完成')
        this.$router.push('/admin/device')
      }
    },
    
    // 设备创建成功回调
    handleDeviceCreated(deviceId) {
      this.deviceId = deviceId
      this.completedTabs.push('basic')
    }
  }
}
</script>

<style scoped>
.device-detail-page {
  padding: 20px;
}
</style>
