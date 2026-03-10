<template>
  <div class="page-content">
    <div class="page-header">操作日志</div>
    <div class="page-body">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input placeholder="操作对象" v-model="filters.object" size="small" style="width: 150px; margin-right: 10px;"></el-input>
        <el-input placeholder="账号" v-model="filters.account" size="small" style="width: 150px; margin-right: 10px;"></el-input>
        <el-select v-model="filters.type" placeholder="操作类型" size="small" style="width: 150px; margin-right: 10px;">
          <el-option label="操作类型" value=""></el-option>
          <el-option label="写入设置" value="write_setting"></el-option>
          <el-option label="登录账号" value="view_log"></el-option>
          <el-option label="绑定网关" value="delete_gateway"></el-option>
          <el-option label="移除网关" value="delete_app"></el-option>
          <el-option label="清除数据" value="delete_group"></el-option>
          <el-option label="固件升级" value="add_node"></el-option>
          <el-option label="恢复出厂设置" value="factory_config"></el-option>
        </el-select>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="起始日期"
          end-placeholder="结束日期"
          size="small"
          style="width: 250px; margin-right: 10px;">
        </el-date-picker>
        <el-button type="primary" size="small" icon="el-icon-search" @click="handleSearch">搜索</el-button>
        <el-button size="small" icon="el-icon-download" style="float: right;">导出记录</el-button>
      </div>

      <!-- 表格 -->
      <el-table :data="logs" v-loading="loading" style="width: 100%" :header-cell-style="{background:'#f5f7fa',color:'#606266'}">
        <el-table-column prop="account" label="操作账号" width="300"></el-table-column>
        <el-table-column prop="object" label="操作对象" width="300"></el-table-column>
        <el-table-column prop="type" label="操作类型" width="500"></el-table-column>
        <el-table-column prop="content" label="操作内容"></el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="180"></el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          background
          layout="total, prev, pager, next, jumper"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          @current-change="handlePageChange">
        </el-pagination>
      </div>
    </div>
  </div>
</template>

<script>
import { getOperationLogs } from '@/api/user'

export default {
  name: 'OperationLogs',
  data() {
    return {
      filters: {
        object: '',
        account: '',
        type: '',
        dateRange: []
      },
      logs: [],
      total: 0,
      page: 1,
      pageSize: 10,
      loading: false
    }
  },
  mounted() {
    this.loadLogs()
  },
  methods: {
    async loadLogs() {
      this.loading = true
      try {
        const params = {
          object: this.filters.object,
          account: this.filters.account,
          type: this.filters.type,
          page: this.page,
          page_size: this.pageSize
        }
        
        if (this.filters.dateRange && this.filters.dateRange.length === 2) {
          params.start_date = this.filters.dateRange[0]
          params.end_date = this.filters.dateRange[1]
        }
        
        const res = await getOperationLogs(params)
        this.logs = res.data.list || []
        this.total = res.data.total || 0
      } catch (error) {
        console.error('加载失败:', error)
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.page = 1
      this.loadLogs()
    },
    handlePageChange(page) {
      this.page = page
      this.loadLogs()
    }
  }
}
</script>

<style scoped>
.page-content {
  padding: 20px;
}

.page-header {
  font-size: 18px;
  color: #333;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>
