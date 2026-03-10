<template>
  <div class="page-content">
    <div class="page-header">未读消息</div>
    <div class="page-body">
      <el-tabs v-model="activeTab" class="message-tabs">
        <el-tab-pane label="全部消息" name="all"></el-tab-pane>
        <el-tab-pane label="报警消息" name="reserved"></el-tab-pane>
        <el-tab-pane label="工单消息" name="workorder"></el-tab-pane>
        <el-tab-pane label="到期提醒" name="expire"></el-tab-pane>
        <el-tab-pane label="系统公告" name="system"></el-tab-pane>
      </el-tabs>

      <div class="action-bar">
        <div class="left-actions">
          <el-checkbox v-model="selectAll" @change="handleSelectAll" style="margin-right: 15px;">全选</el-checkbox>
          <el-button size="small" @click="handleMarkRead" :disabled="selectedMessages.length === 0">标记已读</el-button>
          <el-button size="small" @click="handleMarkAllRead">全部已读</el-button>
          <el-button size="small" type="danger" plain @click="handleBatchDelete" :disabled="selectedMessages.length === 0">删除</el-button>
        </div>
      </div>

      <el-table
        ref="messageTable"
        :data="messageList"
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="{background:'#f5f7fa',color:'#606266'}"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="title" label="消息标题" width="700">
          <template slot-scope="scope">
            <span class="message-dot">•</span>
            {{ scope.row.title }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="500">
           <template slot-scope="scope">
            <span class="text-danger">{{ scope.row.status }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="发布时间" width="500"></el-table-column>
        <el-table-column prop="type" label="类型" width="400"></el-table-column>
        <el-table-column label="操作" width="100">
          <template slot-scope="scope">
            <el-button type="text" class="text-danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && messageList.length === 0" style="text-align: center; padding: 40px 0; color: #909399;">
        暂无数据
      </div>

      <div class="pagination-container">
        <div class="left-pagination-info">
          共 {{ total }} 条，每页显示：
          <el-select v-model="pageSize" size="mini" style="width: 70px" @change="handleSizeChange">
            <el-option label="10" :value="10"></el-option>
            <el-option label="20" :value="20"></el-option>
            <el-option label="50" :value="50"></el-option>
          </el-select>
          条
        </div>
        <el-pagination
          background
          layout="prev, pager, next, jumper"
          :total="total"
          :page-size="pageSize"
          :current-page.sync="currentPage"
          @current-change="handleCurrentChange">
        </el-pagination>
        <span class="page-jump-suffix">前往 <el-input size="mini" style="width: 40px" v-model.number="jumpPage" @keyup.enter.native="handleJump"></el-input> 页</span>
      </div>
    </div>
  </div>
</template>

<script>
import { getMessages, markRead, markAllRead, deleteMessages } from '@/api/message'

export default {
  name: 'UnreadMessages',
  data() {
    return {
      activeTab: 'all',
      pageSize: 10,
      currentPage: 1,
      total: 0,
      jumpPage: 1,
      selectAll: false,
      messageList: [],
      selectedMessages: [],
      loading: false
    }
  },
  mounted() {
    this.loadMessages()
  },
  watch: {
    activeTab() {
      this.currentPage = 1
      this.loadMessages()
    },
    selectAll(val) {
      if (val) {
        this.$refs.messageTable.toggleAllSelection()
      } else {
        this.$refs.messageTable.clearSelection()
      }
    }
  },
  methods: {
    async loadMessages() {
      this.loading = true
      try {
        const res = await getMessages({
          type: this.activeTab,
          is_read: false,
          page: this.currentPage,
          page_size: this.pageSize
        })
        this.messageList = res.data.list || []
        this.total = res.data.total || 0
      } catch (error) {
        console.error('加载失败:', error)
      } finally {
        this.loading = false
      }
    },
    handleSelectionChange(val) {
      this.selectedMessages = val
      this.selectAll = val.length === this.messageList.length && val.length > 0
    },
    handleSelectAll(val) {
      if (val) {
        this.$refs.messageTable.toggleAllSelection()
      } else {
        this.$refs.messageTable.clearSelection()
      }
    },
    async handleMarkRead() {
      if (this.selectedMessages.length === 0) return
      try {
        await markRead(this.selectedMessages.map(m => m.id))
        this.$message.success('标记成功')
        this.loadMessages()
        this.$store.dispatch('fetchUnreadCount')
      } catch (error) {
        console.error('标记失败:', error)
      }
    },
    async handleMarkAllRead() {
      try {
        await markAllRead(this.activeTab)
        this.$message.success('全部已读')
        this.loadMessages()
        this.$store.dispatch('fetchUnreadCount')
      } catch (error) {
        console.error('操作失败:', error)
      }
    },
    async handleDelete(id) {
      this.$confirm('确定要删除这条消息吗?', '提示', {
        type: 'warning'
      }).then(async () => {
        try {
          await deleteMessages([id])
          this.$message.success('删除成功')
          this.loadMessages()
        } catch (error) {
          console.error('删除失败:', error)
        }
      }).catch(() => {})
    },
    async handleBatchDelete() {
      if (this.selectedMessages.length === 0) return
      this.$confirm(`确定要删除选中的${this.selectedMessages.length}条消息吗?`, '提示', {
        type: 'warning'
      }).then(async () => {
        try {
          await deleteMessages(this.selectedMessages.map(m => m.id))
          this.$message.success('删除成功')
          this.loadMessages()
        } catch (error) {
          console.error('删除失败:', error)
        }
      }).catch(() => {})
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.loadMessages()
    },
    handleCurrentChange(val) {
      this.jumpPage = val
      this.loadMessages()
    },
    handleJump() {
      if (this.jumpPage > 0 && this.jumpPage <= Math.ceil(this.total / this.pageSize)) {
        this.currentPage = this.jumpPage
        this.loadMessages()
      } else {
        this.jumpPage = this.currentPage
        this.$message.warning('请输入有效的页码')
      }
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

.message-tabs {
  margin-bottom: 10px;
}

.action-bar {
  margin-bottom: 15px;
}

.message-dot {
  color: #409EFF;
  font-size: 20px;
  margin-right: 5px;
  vertical-align: middle;
  line-height: 1;
}

.text-danger {
  color: #F56C6C;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.left-pagination-info {
  font-size: 13px;
  color: #606266;
  margin-right: 10px;
}

.page-jump-suffix {
  font-size: 13px;
  color: #606266;
  margin-left: 10px;
  display: flex;
  align-items: center;
}
</style>
