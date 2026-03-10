<template>
  <div class="variables-manage-tab">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input v-model="searchName" placeholder="变量名称、地址、键值(key)" style="width: 280px; margin-right: 10px;" size="small"></el-input>
      <el-select v-model="searchDriver" placeholder="所有驱动" style="width: 150px; margin-right: 10px;" size="small" clearable>
        <el-option label="所有驱动" value=""></el-option>
      </el-select>
      <el-select v-model="searchType" placeholder="所有类型" style="width: 150px; margin-right: 10px;" size="small" clearable>
        <el-option label="所有类型" value=""></el-option>
      </el-select>
      <el-button type="primary" icon="el-icon-search" size="small" @click="handleSearch">搜索</el-button>
      <el-button type="text" size="small">高级搜索</el-button>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div>
        <el-dropdown trigger="click" @command="handleCommand" style="margin-right: 10px;">
          <el-button type="primary" size="small">
            通过口配置导入<i class="el-icon-arrow-down el-icon--right"></i>
          </el-button>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item command="import">导入</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
        <el-button type="primary" icon="el-icon-plus" size="small" @click="handleAdd">新增</el-button>
        <el-button icon="el-icon-delete" size="small" @click="handleBatchDelete" :disabled="selectedVars.length === 0">删除</el-button>
      </div>
      <div style="color: #606266;">变量列表({{ total }})</div>
    </div>

    <!-- 表格 -->
    <el-table :data="variableList" @selection-change="handleSelectionChange" style="width: 100%;">
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column prop="var_name" label="名称" min-width="150"></el-table-column>
      <el-table-column prop="slave_address" label="从站地址" width="100"></el-table-column>
      <el-table-column prop="data_type" label="数据类型" width="150"></el-table-column>
      <el-table-column prop="register_type" label="寄存器类型" width="150"></el-table-column>
      <el-table-column prop="read_write" label="读写类型" width="100"></el-table-column>
      <el-table-column prop="address" label="地址" width="100"></el-table-column>
      <el-table-column prop="key_name" label="键值(key)" width="120"></el-table-column>
      <el-table-column prop="driver_name" label="网关驱动" width="120"></el-table-column>
      <el-table-column prop="collect_mode" label="采集方式" width="120"></el-table-column>
      <el-table-column label="操作" fixed="right" width="250">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <span class="separator">|</span>
          <el-button type="text" size="small" @click="handleCopy(scope.row)">复制</el-button>
          <span class="separator">|</span>
          <el-button type="text" size="small" @click="handleViewData(scope.row)">查看数据</el-button>
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

    <!-- 分页和按钮 -->
    <div class="footer-actions">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="color: #606266;">共有{{ total }}条</div>
        <el-pagination
          background
          layout="prev, pager, next, sizes, jumper"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          @size-change="handleSizeChange"
          @current-change="handlePageChange">
        </el-pagination>
      </div>
      <div style="margin-top: 20px;">
        <el-button @click="goBack">上一步</el-button>
        <el-button type="primary" @click="handleNext">保存并下一步</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { getDeviceVariables } from '@/api/deviceDetail'

export default {
  name: 'VariablesManage',
  props: {
    deviceId: Number,
    mode: String
  },
  data() {
    return {
      variableList: [],
      selectedVars: [],
      searchName: '',
      searchDriver: '',
      searchType: '',
      total: 0,
      pageSize: 20,
      currentPage: 1
    }
  },
  created() {
    this.fetchVariables()
  },
  methods: {
    async fetchVariables() {
      if (!this.deviceId) {
        console.warn('deviceId is null, skip loading')
        return
      }
      try {
        const res = await getDeviceVariables(this.deviceId, { 
          page: this.currentPage, 
          page_size: this.pageSize 
        })
        this.variableList = res.data || []
        // TODO: 后端返回TOTAL
        this.total = this.variableList.length
      } catch (error) {
        console.error('加载变量失败:', error)
        if (error.response?.status !== 404) {
          this.$message.error('加载变量失败')
        }
      }
    },
    handleSelectionChange(selection) {
      this.selectedVars = selection
    },
    handleSearch() {
      this.currentPage = 1
      this.fetchVariables()
    },
    handleCommand(command) {
      if (command === 'import') {
        this.$message.info('导入功能待实现')
      }
    },
    handleAdd() {
      this.$message.info('新增功能待实现')
    },
    handleBatchDelete() {
      this.$message.info('批量删除功能待实现')
    },
    handleEdit() {
      this.$message.info('编辑功能待实现')
    },
    handleCopy() {
      this.$message.info('复制功能待实现')
    },
    handleViewData() {
      this.$message.info('查看数据功能待实现')
    },
    handleRowCommand(command) {
      if (command === 'delete') {
        this.$message.info('删除功能待实现')
      }
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.fetchVariables()
    },
    handlePageChange(page) {
      this.currentPage = page
      this.fetchVariables()
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
