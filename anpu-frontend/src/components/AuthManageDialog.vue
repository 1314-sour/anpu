<template>
  <el-dialog
    title="账号授权管理"
    :visible.sync="dialogVisible"
    width="1100px"
    :close-on-click-modal="false"
    @close="handleClose">
    
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchForm.keyword"
        placeholder="账号、联系人"
        style="width: 200px; margin-right: 10px;"
        size="small">
      </el-input>
      
      <el-select
        v-model="searchForm.department"
        placeholder="安普科技有限公司"
        style="width: 150px; margin-right: 10px;"
        size="small"
        clearable>
        <el-option label="安普科技有限公司" value="安普科技有限公司"></el-option>
        <el-option label="技术部" value="技术部"></el-option>
        <el-option label="工程部" value="工程部"></el-option>
        <el-option label="运维部" value="运维部"></el-option>
        <el-option label="售后部" value="售后部"></el-option>
        <el-option label="市场部" value="市场部"></el-option>
      </el-select>
      
      <el-button type="primary" size="small" @click="handleSearch">搜索</el-button>
      
      <el-button 
        type="primary" 
        icon="el-icon-plus" 
        size="small" 
        style="float: right;"
        @click="handleAdd">
        新增
      </el-button>
    </div>
    
    <!-- 表格 -->
    <el-table
      :data="tableData"
      style="width: 100%; margin-top: 15px;"
      :header-cell-style="{background:'#f5f7fa',color:'#606266'}"
      @selection-change="handleSelectionChange">
      <el-table-column
        type="selection"
        width="50">
      </el-table-column>
      
      <el-table-column
        prop="account"
        label="账号"
        min-width="120">
      </el-table-column>
      
      <el-table-column
        prop="contact"
        label="联系人"
        min-width="100">
      </el-table-column>
      
      <el-table-column
        prop="department"
        label="部门"
        min-width="100">
      </el-table-column>
      
      <el-table-column
        prop="role"
        label="角色"
        min-width="100">
      </el-table-column>
      
      <el-table-column
        prop="appWechat"
        label="APP/微信"
        min-width="100">
        <template slot-scope="scope">
          <el-switch
            v-model="scope.row.appWechat"
            @change="handleSwitchChange(scope.row, 'appWechat')">
          </el-switch>
        </template>
      </el-table-column>
      
      <el-table-column
        prop="smsPush"
        label="短信推送"
        min-width="100">
        <template slot-scope="scope">
          <el-switch
            v-model="scope.row.smsPush"
            @change="handleSwitchChange(scope.row, 'smsPush')">
          </el-switch>
        </template>
      </el-table-column>
      
      <el-table-column
        prop="pagePermission"
        label="页面权限"
        min-width="100">
      </el-table-column>
      
      <el-table-column
        label="操作"
        width="80"
        fixed="right">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 空数据提示 -->
    <div v-if="tableData.length === 0" class="empty-data">
      暂无数据
    </div>
    
    <!-- 底部操作和分页 -->
    <div class="footer-bar">
      <div class="footer-left">
        <el-checkbox v-model="selectAll" @change="handleSelectAll">全选</el-checkbox>
        <el-button 
          type="primary" 
          size="small" 
          :disabled="selectedRows.length === 0"
          @click="handleBatchEdit">
          批量编辑
        </el-button>
        <el-button 
          size="small" 
          :disabled="selectedRows.length === 0"
          @click="handleCancelAuth">
          取消授权
        </el-button>
      </div>
      
      <div class="footer-right">
        <span style="margin-right: 10px; color: #606266;">共有{{ total }}条，每页显示：</span>
        <el-select v-model="pageSize" size="small" style="width: 80px;" @change="handlePageSizeChange">
          <el-option label="10条" :value="10"></el-option>
          <el-option label="20条" :value="20"></el-option>
          <el-option label="50条" :value="50"></el-option>
        </el-select>
        
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handleCurrentChange"
          style="display: inline-block; margin-left: 10px;">
        </el-pagination>
        
        <span style="margin-left: 10px; color: #606266;">前往</span>
        <el-input
          v-model.number="jumpPage"
          size="small"
          style="width: 50px; margin: 0 5px;"
          @keyup.enter.native="handleJumpPage">
        </el-input>
        <span style="color: #606266;">页</span>
      </div>
    </div>
  </el-dialog>
</template>

<script>
export default {
  name: 'AuthManageDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    deviceId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      searchForm: {
        keyword: '',
        department: '安普科技有限公司'
      },
      tableData: [],
      total: 0,
      pageSize: 10,
      currentPage: 1,
      jumpPage: 1,
      selectAll: false,
      selectedRows: []
    }
  },
  computed: {
    dialogVisible: {
      get() {
        return this.visible
      },
      set(val) {
        this.$emit('update:visible', val)
      }
    }
  },
  methods: {
    handleClose() {
      this.dialogVisible = false
      this.resetData()
    },
    handleSearch() {
      // 调用搜索API
      this.loadData()
    },
    handleAdd() {
      // 打开新增授权弹窗
      this.$message.info('打开新增授权弹窗')
    },
    handleEdit(row) {
      // 编辑授权
      this.$message.info(`编辑账号：${row.account}`)
    },
    handleBatchEdit() {
      // 批量编辑
      this.$message.info(`批量编辑 ${this.selectedRows.length} 条记录`)
    },
    handleCancelAuth() {
      // 取消授权
      this.$confirm(`确定要取消选中的 ${this.selectedRows.length} 个账号的授权吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$message.success('取消授权成功')
        this.loadData()
      }).catch(() => {})
    },
    handleSelectionChange(selection) {
      this.selectedRows = selection
      this.selectAll = selection.length === this.tableData.length && this.tableData.length > 0
    },
    handleSelectAll(val) {
      if (val) {
        this.$refs.table && this.$refs.table.toggleAllSelection()
      } else {
        this.$refs.table && this.$refs.table.clearSelection()
      }
    },
    handleSwitchChange(row, field) {
      // 处理开关变化
      this.$message.success(`已${row[field] ? '开启' : '关闭'}${field === 'appWechat' ? 'APP/微信' : '短信推送'}`)
    },
    handlePageSizeChange(val) {
      this.pageSize = val
      this.loadData()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.loadData()
    },
    handleJumpPage() {
      if (this.jumpPage >= 1 && this.jumpPage <= Math.ceil(this.total / this.pageSize)) {
        this.currentPage = this.jumpPage
        this.loadData()
      }
    },
    loadData() {
      // 这里调用API加载授权账号列表
      // 示例数据（实际应从API获取）
      /*
      this.tableData = [
        {
          id: 1,
          account: 'user001',
          contact: '张三',
          department: '技术部',
          role: '管理员',
          appWechat: true,
          smsPush: false,
          pagePermission: '全部'
        }
      ]
      this.total = 0
      */
    },
    resetData() {
      this.searchForm = {
        keyword: '',
        department: '技术部'
      }
      this.tableData = []
      this.selectedRows = []
      this.selectAll = false
      this.currentPage = 1
    }
  },
  watch: {
    visible(val) {
      if (val) {
        this.loadData()
      } else {
        this.resetData()
      }
    }
  }
}
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
}

.empty-data {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  font-size: 14px;
}

.footer-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-right {
  display: flex;
  align-items: center;
}

::v-deep .el-table__empty-text {
  display: none;
}
</style>
