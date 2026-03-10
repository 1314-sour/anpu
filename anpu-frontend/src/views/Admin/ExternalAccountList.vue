<template>
  <div class="external-account-page">
    <!-- 搜索和操作栏 -->
    <div class="filter-container">
      <el-input 
        v-model="searchForm.keyword" 
        placeholder="用户名、联系人、联系电话" 
        style="width: 200px; margin-right: 10px;" 
        size="small">
      </el-input>
      
      <el-input 
        v-model="searchForm.company" 
        placeholder="企业名称" 
        style="width: 150px; margin-right: 10px;" 
        size="small"
        clearable>
      </el-input>
      
      <el-input 
        v-model="searchForm.role" 
        placeholder="角色" 
        style="width: 120px; margin-right: 10px;" 
        size="small"
        clearable>
      </el-input>
      
      <el-button type="primary" icon="el-icon-search" size="small" @click="handleSearch">搜索</el-button>
      
      <el-checkbox v-model="onlyMyCreated" style="margin-left: 10px;" size="small">由我创建</el-checkbox>

      <div class="right-actions" style="float: right;">
        <el-button type="primary" icon="el-icon-plus" size="small" @click="handleAdd">新增</el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table 
      :data="tableData" 
      style="width: 100%; margin-top: 15px;"
      :header-cell-style="{background:'#f5f7fa',color:'#606266'}">
      <el-table-column prop="username" label="用户名" min-width="120"></el-table-column>
      <el-table-column prop="role" label="角色" min-width="100"></el-table-column>
      <el-table-column prop="contact" label="联系人" min-width="100"></el-table-column>
      <el-table-column prop="contactPhone" label="联系电话" min-width="120"></el-table-column>
      <el-table-column prop="department" label="部门" min-width="100"></el-table-column>
      <el-table-column prop="companyName" label="企业名称" min-width="150"></el-table-column>
      <el-table-column prop="packageAccount" label="包裹账号" min-width="100"></el-table-column>
      <el-table-column prop="detailAddress" label="详细地址" min-width="150"></el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 空数据提示 -->
    <div v-if="tableData.length === 0" class="empty-data">
      暂无数据
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <span class="total-info">共有{{ total }}条</span>
      <el-select v-model="pageSize" size="small" style="width: 100px; margin: 0 10px;" @change="handlePageSizeChange">
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
        @current-change="handleCurrentChange">
      </el-pagination>
      
      <span style="margin-left: 10px;">前往</span>
      <el-input
        v-model.number="jumpPage"
        size="small"
        style="width: 50px; margin: 0 5px;"
        @keyup.enter.native="handleJumpPage">
      </el-input>
      <span>页</span>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      :title="dialogTitle"
      :visible.sync="dialogVisible"
      width="600px"
      :close-on-click-modal="false"
      @close="handleDialogClose">
      <el-form :model="form" :rules="rules" ref="accountForm" label-width="120px">
        <el-form-item label="用户名：" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        
        <el-form-item label="角色：" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%;">
            <el-option label="管理员" value="管理员"></el-option>
            <el-option label="普通用户" value="普通用户"></el-option>
            <el-option label="访客" value="访客"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="联系人：" prop="contact">
          <el-input v-model="form.contact" placeholder="请输入联系人"></el-input>
        </el-form-item>
        
        <el-form-item label="联系电话：" prop="contactPhone">
          <el-input v-model="form.contactPhone" placeholder="请输入联系电话"></el-input>
        </el-form-item>
        
        <el-form-item label="部门：" prop="department">
          <el-input v-model="form.department" placeholder="请输入部门"></el-input>
        </el-form-item>
        
        <el-form-item label="企业名称：" prop="companyName">
          <el-input v-model="form.companyName" placeholder="请输入企业名称"></el-input>
        </el-form-item>
        
        <el-form-item label="包裹账号：" prop="packageAccount">
          <el-input v-model="form.packageAccount" placeholder="请输入包裹账号"></el-input>
        </el-form-item>
        
        <el-form-item label="详细地址：" prop="detailAddress">
          <el-input v-model="form.detailAddress" type="textarea" :rows="3" placeholder="请输入详细地址"></el-input>
        </el-form-item>
      </el-form>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleSubmit">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ExternalAccountList',
  data() {
    return {
      searchForm: {
        keyword: '',
        company: '',
        role: ''
      },
      onlyMyCreated: false,
      tableData: [],
      total: 0,
      pageSize: 10,
      currentPage: 1,
      jumpPage: 1,
      
      dialogVisible: false,
      dialogTitle: '新增账号',
      form: {
        id: null,
        username: '',
        role: '',
        contact: '',
        contactPhone: '',
        department: '',
        companyName: '',
        packageAccount: '',
        detailAddress: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        role: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ],
        contact: [
          { required: true, message: '请输入联系人', trigger: 'blur' }
        ],
        contactPhone: [
          { required: true, message: '请输入联系电话', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
        ],
        companyName: [
          { required: true, message: '请输入企业名称', trigger: 'blur' }
        ]
      }
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    handleSearch() {
      this.currentPage = 1
      this.loadData()
    },
    handleAdd() {
      this.dialogTitle = '新增账号'
      this.form = {
        id: null,
        username: '',
        role: '',
        contact: '',
        contactPhone: '',
        department: '',
        companyName: '',
        packageAccount: '',
        detailAddress: ''
      }
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs.accountForm && this.$refs.accountForm.clearValidate()
      })
    },
    handleEdit(row) {
      this.dialogTitle = '编辑账号'
      this.form = { ...row }
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs.accountForm && this.$refs.accountForm.clearValidate()
      })
    },
    handleSubmit() {
      this.$refs.accountForm.validate((valid) => {
        if (valid) {
          // TODO: 调用API保存数据
          if (this.form.id) {
            this.$message.success('更新成功')
          } else {
            this.$message.success('新增成功')
          }
          this.dialogVisible = false
          this.loadData()
        }
      })
    },
    handleDialogClose() {
      this.$refs.accountForm && this.$refs.accountForm.resetFields()
    },
    handlePageSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
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
      // TODO: 调用API加载数据
      // 示例数据
      this.tableData = []
      this.total = 0
    }
  }
}
</script>

<style scoped>
.external-account-page {
  padding: 0;
}

.filter-container {
  margin-bottom: 15px;
}

.right-actions {
  float: right;
}

.empty-data {
  text-align: center;
  padding: 60px 0;
  color: #909399;
  font-size: 14px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.total-info {
  margin-right: 10px;
  color: #606266;
  font-size: 14px;
}
</style>
