<template>
  <div class="alarms-manage-tab">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input v-model="searchName" placeholder="请输入内容关键字" style="width: 200px; margin-right: 10px;" size="small"></el-input>
      <el-button type="primary" icon="el-icon-search" size="small" @click="handleSearch">搜索</el-button>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div>
        <el-button type="text" size="small" @click="handleToggleView">
          <i :class="viewMode === 'list' ? 'el-icon-s-grid' : 'el-icon-menu'"></i>
          {{ viewMode === 'list' ? '列表' : '网格' }}
        </el-button>
        <el-button type="primary" icon="el-icon-plus" size="small" @click="handleAdd" style="margin-left: 10px;">新增页面</el-button>
      </div>
      <div style="color: #606266;">报告管理({{ alarmList.length }})</div>
    </div>

    <!-- 表格视图 -->
    <el-table v-if="viewMode === 'list'" :data="alarmList" style="width: 100%;">
      <el-table-column prop="alarm_name" label="页面名称" min-width="200"></el-table-column>
      <el-table-column prop="resolution" label="分辨率" width="150"></el-table-column>
      <el-table-column prop="page_type" label="页面类型" width="150"></el-table-column>
      <el-table-column label="操作" fixed="right" width="150">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <span class="separator">|</span>
          <el-dropdown trigger="click" @command="(cmd) => handleRowCommand(cmd, scope.row)">
            <span class="el-dropdown-link">
              <i class="el-icon-more" style="cursor: pointer; color: #409EFF;"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="delete">删除</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <!-- 网格视图 -->
    <div v-else class="grid-view">
      <div v-for="item in alarmList" :key="item.id" class="grid-item">
        <div class="grid-item-content">
          <i class="el-icon-document" style="font-size: 48px; color: #909399;"></i>
          <div class="grid-item-name">{{ item.alarm_name }}</div>
          <div class="grid-item-info">{{ item.resolution }}</div>
        </div>
        <div class="grid-item-actions">
          <el-button type="text" size="small" @click="handleEdit(item)">编辑</el-button>
          <el-button type="text" size="small" @click="handleDelete(item)">删除</el-button>
        </div>
      </div>
    </div>

    <!-- 底部按钮 -->
    <div class="footer-actions">
      <el-button @click="goBack">上一步</el-button>
      <el-button type="primary" @click="handleFinish">完成</el-button>
    </div>
  </div>
</template>

<script>
import { getDeviceAlarms } from '@/api/deviceDetail'

export default {
  name: 'AlarmsManage',
  props: {
    deviceId: Number,
    mode: String
  },
  data() {
    return {
      alarmList: [],
      searchName: '',
      viewMode: 'list' // 'list' 或 'grid'
    }
  },
  created() {
    this.fetchAlarms()
  },
  methods: {
    async fetchAlarms() {
      if (!this.deviceId) {
        console.warn('deviceId is null, skip loading')
        return
      }
      try {
        const res = await getDeviceAlarms(this.deviceId)
        this.alarmList = res.data || []
      } catch (error) {
        console.error('加载报告失败:', error)
        if (error.response?.status !== 404) {
          this.$message.error('加载报告失败')
        }
      }
    },
    handleSearch() {
      this.fetchAlarms()
    },
    handleToggleView() {
      this.viewMode = this.viewMode === 'list' ? 'grid' : 'list'
    },
    handleAdd() {
      this.$message.info('新增页面功能待实现')
    },
    handleEdit() {
      this.$message.info('编辑功能待实现')
    },
    handleRowCommand(command) {
      if (command === 'delete') {
        this.$message.info('删除功能待实现')
      }
    },
    handleDelete() {
      this.$message.info('删除功能待实现')
    },
    handleFinish() {
      this.$message.success('设备配置完成')
      this.$router.push('/admin/device-list')
    },
    goBack() {
      this.$router.back()
    }
  }
}
</script>

<style scoped>
.search-bar {
  margin-bottom: 15px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.separator {
  margin: 0 5px;
  color: #dcdfe6;
}

.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.grid-item {
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  padding: 20px;
  text-align: center;
  transition: all 0.3s;
}

.grid-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.grid-item-content {
  margin-bottom: 15px;
}

.grid-item-name {
  font-size: 14px;
  font-weight: bold;
  margin: 10px 0 5px;
  color: #303133;
}

.grid-item-info {
  font-size: 12px;
  color: #909399;
}

.grid-item-actions {
  border-top: 1px solid #EBEEF5;
  padding-top: 10px;
}

.footer-actions {
  margin-top: 20px;
}
</style>
