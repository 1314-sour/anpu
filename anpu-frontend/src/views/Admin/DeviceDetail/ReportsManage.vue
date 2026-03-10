<template>
  <div class="reports-manage-tab">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input v-model="searchName" placeholder="请输入关键字" style="width: 200px; margin-right: 10px;" size="small"></el-input>
      <el-button type="primary" icon="el-icon-search" size="small" @click="handleSearch">搜索</el-button>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" icon="el-icon-plus" size="small" @click="handleAdd">新增</el-button>
      <div style="color: #606266;">历史报表管理({{ reportList.length }})</div>
    </div>

    <!-- 表格 -->
    <el-table :data="reportList" style="width: 100%;">
      <el-table-column type="index" label="ID" width="80"></el-table-column>
      <el-table-column prop="report_name" label="名称" min-width="200"></el-table-column>
      <el-table-column prop="report_type" label="报表类型" width="150"></el-table-column>
      <el-table-column prop="variable_count" label="关联变量数" width="120"></el-table-column>
      <el-table-column label="操作" fixed="right" width="200">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleViewData(scope.row)">数据查询</el-button>
          <span class="separator">|</span>
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

    <!-- 底部按钮 -->
    <div class="footer-actions">
      <el-button @click="goBack">上一步</el-button>
      <el-button type="primary" @click="handleNext">保存并下一步</el-button>
    </div>
  </div>
</template>

<script>
import { getDeviceReports } from '@/api/deviceDetail'

export default {
  name: 'ReportsManage',
  props: {
    deviceId: Number,
    mode: String
  },
  data() {
    return {
      reportList: [],
      searchName: ''
    }
  },
  created() {
    this.fetchReports()
  },
  methods: {
    async fetchReports() {
      if (!this.deviceId) {
        console.warn('deviceId is null, skip loading')
        return
      }
      try {
        const res = await getDeviceReports(this.deviceId)
        this.reportList = res.data || []
      } catch (error) {
        console.error('加载报表失败:', error)
        if (error.response?.status !== 404) {
          this.$message.error('加载报表失败')
        }
      }
    },
    handleSearch() {
      this.fetchReports()
    },
    handleAdd() {
      this.$message.info('新增功能待实现')
    },
    handleViewData() {
      this.$message.info('数据查询功能待实现')
    },
    handleEdit() {
      this.$message.info('编辑功能待实现')
    },
    handleRowCommand(command) {
      if (command === 'delete') {
        this.$message.info('删除功能待实现')
      }
    },
    handleNext() {
      this.$emit('next')
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

.footer-actions {
  margin-top: 20px;
}
</style>
