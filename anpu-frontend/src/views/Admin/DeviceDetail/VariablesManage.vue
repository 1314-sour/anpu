<template>
  <div class="variables-manage-tab">
    <el-alert
      title="变量管理用于定义采集点位。变量名称与寄存器地址在同一驱动内需保持唯一，避免采集冲突。"
      type="info"
      :closable="false"
      class="tips-alert"
    ></el-alert>

    <div class="search-bar">
      <el-input
        v-model="searchForm.keyword"
        placeholder="搜索名称/寄存器地址"
        clearable
        size="small"
        class="w-240"
      ></el-input>
      <el-select v-model="searchForm.driverId" placeholder="所属驱动" clearable size="small" class="w-180">
        <el-option v-for="item in drivers" :key="item.id" :label="item.name" :value="item.id"></el-option>
      </el-select>
      <el-select v-model="searchForm.variableType" placeholder="变量类型" clearable size="small" class="w-160">
        <el-option
          v-for="item in variableTypeOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        ></el-option>
      </el-select>
      <el-select v-model="searchForm.cycleCollect" placeholder="周期采集" clearable size="small" class="w-140">
        <el-option label="开启" value="on"></el-option>
        <el-option label="关闭" value="off"></el-option>
      </el-select>
      <el-button type="primary" icon="el-icon-search" size="small" @click="handleSearch">搜索</el-button>
      <el-button size="small" @click="resetSearch">重置</el-button>
    </div>

    <div class="action-bar">
      <div>
        <el-button type="primary" icon="el-icon-plus" size="small" @click="openCreateDialog">新增变量</el-button>
        <el-button icon="el-icon-delete" size="small" :disabled="selectedVars.length === 0" @click="handleBatchDelete">批量删除</el-button>
      </div>
      <div class="stat-text">变量列表（{{ total }}）</div>
    </div>

    <el-table v-loading="loading" :data="pageData" @selection-change="handleSelectionChange" border>
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column prop="name" label="名称" min-width="180" show-overflow-tooltip></el-table-column>
      <el-table-column prop="registerAddress" label="寄存器地址" min-width="120"></el-table-column>
      <el-table-column prop="dataTypeLabel" label="数据类型" min-width="120"></el-table-column>
      <el-table-column prop="registerTypeLabel" label="寄存器类型" min-width="120"></el-table-column>
      <el-table-column prop="readWriteLabel" label="读写类型" min-width="100"></el-table-column>
      <el-table-column label="实时数据" min-width="120" align="center">
        <template slot-scope="scope">
          <strong style="color: #409EFF; font-size: 16px;">
            {{ scope.row.currentValue }}
          </strong>
        </template>
      </el-table-column>
      <el-table-column prop="cycleCollectLabel" label="周期采集" min-width="100">
        <template slot-scope="scope">
          <el-tag :type="scope.row.cycleCollect === 'on' ? 'success' : 'info'" size="mini">
            {{ scope.row.cycleCollectLabel }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="driverName" label="所属驱动" min-width="120" show-overflow-tooltip></el-table-column>
      <el-table-column prop="variableTypeLabel" label="变量类型" min-width="120"></el-table-column>
      <el-table-column label="操作" fixed="right" width="220">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <span class="separator">|</span>
          <el-button type="text" size="small" @click="handleCopy(scope.row)">复制</el-button>
          <span class="separator">|</span>
          <el-button type="text" size="small" class="danger-text" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="footer-actions">
      <div class="pagination-wrap">
        <div class="stat-text">共有 {{ total }} 条</div>
        <el-pagination
          background
          layout="prev, pager, next, sizes, jumper"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          :current-page="currentPage"
          @size-change="handleSizeChange"
          @current-change="handlePageChange">
        </el-pagination>
      </div>
      <div class="step-actions">
        <el-button @click="goBack">上一步</el-button>
        <el-button type="primary" @click="handleNext">保存并下一步</el-button>
      </div>
    </div>

    <el-dialog
      :title="dialogMode === 'create' ? '新增变量' : '编辑变量'"
      :visible.sync="dialogVisible"
      width="680px"
      :close-on-click-modal="false"
      @close="resetDialog"
    >
      <el-form ref="variableForm" :model="variableForm" :rules="variableRules" label-width="110px" class="variable-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="名称" prop="name">
              <el-input v-model.trim="variableForm.name" maxlength="60" show-word-limit placeholder="请输入变量名称"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="寄存器地址" prop="registerAddress">
              <el-input v-model.trim="variableForm.registerAddress" placeholder="例如：40001"></el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="数据类型" prop="dataType">
              <el-select v-model="variableForm.dataType" placeholder="请选择" style="width: 100%;">
                <el-option v-for="item in dataTypeOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="寄存器类型" prop="registerType">
              <el-select v-model="variableForm.registerType" placeholder="请选择" style="width: 100%;">
                <el-option v-for="item in registerTypeOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="读写类型" prop="readWrite">
              <el-select v-model="variableForm.readWrite" placeholder="请选择" style="width: 100%;">
                <el-option v-for="item in readWriteOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="周期采集" prop="cycleCollect">
              <el-radio-group v-model="variableForm.cycleCollect">
                <el-radio-button label="on">开启</el-radio-button>
                <el-radio-button label="off">关闭</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="所属驱动" prop="driverId">
              <el-select v-model="variableForm.driverId" placeholder="请选择" style="width: 100%;" filterable>
                <el-option v-for="item in drivers" :key="item.id" :label="item.name" :value="item.id"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="变量类型" prop="variableType">
              <el-select v-model="variableForm.variableType" placeholder="请选择" style="width: 100%;">
                <el-option
                  v-for="item in variableTypeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import {
  getDeviceVariables,
  createDeviceVariable,
  updateDeviceVariable,
  batchDeleteVariables,
  getDeviceDrivers
} from '@/api/deviceDetail'

export default {
  name: 'VariablesManage',
  props: {
    deviceId: Number,
    mode: String,
    gatewaySn: String
  },
  data() {
    return {
      ws: null,
      loading: false,
      submitLoading: false,
      variableList: [],
      filteredList: [],
      pageData: [],
      selectedVars: [],
      drivers: [],
      searchForm: {
        keyword: '',
        driverId: '',
        variableType: '',
        cycleCollect: ''
      },
      total: 0,
      pageSize: 20,
      currentPage: 1,
      dialogVisible: false,
      dialogMode: 'create',
      editingId: null,
      variableForm: {
        name: '',
        registerAddress: '',
        dataType: 'int16',
        registerType: 'holding',
        readWrite: 'read',
        cycleCollect: 'on',
        driverId: '',
        variableType: 'device'
      },
      dataTypeOptions: [
        { label: 'INT16', value: 'int16' },
        { label: 'UINT16', value: 'uint16' },
        { label: 'INT32', value: 'int32' },
        { label: 'UINT32', value: 'uint32' },
        { label: 'FLOAT', value: 'float' },
        { label: 'DOUBLE', value: 'double' },
        { label: 'BOOL', value: 'bool' },
        { label: 'STRING', value: 'string' }
      ],
      registerTypeOptions: [
        { label: '线圈寄存器 (Coil)', value: 'coil' },
        { label: '离散输入寄存器 (Discrete Input)', value: 'discrete_input' },
        { label: '输入寄存器 (Input Register)', value: 'input' },
        { label: '保持寄存器 (Holding Register)', value: 'holding' }
      ],
      readWriteOptions: [
        { label: '只读', value: 'read' },
        { label: '只写', value: 'write' },
        { label: '读写', value: 'read_write' }
      ],
      variableTypeOptions: [
        { label: '设备变量', value: 'device' },
        { label: '中间变量', value: 'middle' },
        { label: '内部变量', value: 'internal' }
      ],
      variableRules: {
        name: [{ required: true, message: '请输入变量名称', trigger: 'blur' }],
        registerAddress: [
          { required: true, message: '请输入寄存器地址', trigger: 'blur' },
          {
            pattern: /^\d+$/,
            message: '寄存器地址必须为非负整数',
            trigger: 'blur'
          }
        ],
        dataType: [{ required: true, message: '请选择数据类型', trigger: 'change' }],
        registerType: [{ required: true, message: '请选择寄存器类型', trigger: 'change' }],
        readWrite: [{ required: true, message: '请选择读写类型', trigger: 'change' }],
        cycleCollect: [{ required: true, message: '请选择周期采集', trigger: 'change' }],
        driverId: [{ required: true, message: '请选择所属驱动', trigger: 'change' }],
        variableType: [{ required: true, message: '请选择变量类型', trigger: 'change' }]
      }
    }
  },
  created() {
    this.initPage()
  },
  mounted() {
    this.initWebSocket() // 页面挂载后去连 WebSocket
  },
  beforeDestroy() {
    if (this.ws) {
      this.ws.close() // 离开页面时掐断连接，防止内存泄漏
    }
  },
  methods: {
    async initPage() {
      await Promise.all([this.fetchDrivers(), this.fetchVariables()])
    },
    getLabelByValue(options, value) {
      const hit = options.find(item => item.value === value)
      return hit ? hit.label : '-'
    },
    normalizeVariable(item) {
      const cycleCollect = item.cycle_collect === false || item.collect_mode === 'off' || item.cycle_collect === 'off'
        ? 'off'
        : 'on'
      const variableType = item.variable_type || 'device'
      const driverId = item.driver_id || item.driverId || ''
      const driverName = item.driver_name || item.driverName || this.getDriverName(driverId)

      return {
        id: item.id,
        name: item.var_name || item.name || '',
        registerAddress: String(item.address ?? item.register_address ?? ''),
        dataType: item.data_type || 'int16',
        dataTypeLabel: this.getLabelByValue(this.dataTypeOptions, item.data_type || 'int16'),
        registerType: item.register_type || 'holding',
        registerTypeLabel: this.getLabelByValue(this.registerTypeOptions, item.register_type || 'holding'),
        readWrite: item.read_write || 'read',
        readWriteLabel: this.getLabelByValue(this.readWriteOptions, item.read_write || 'read'),
        cycleCollect,
        cycleCollectLabel: cycleCollect === 'on' ? '开启' : '关闭',
        driverId,
        driverName,
        variableType,
        variableTypeLabel: this.getLabelByValue(this.variableTypeOptions, variableType)
        currentValue: '--'
      }
    },
    async fetchDrivers() {
      if (!this.deviceId) return
      try {
        const res = await getDeviceDrivers(this.deviceId)
        const list = Array.isArray(res.data) ? res.data : (res.data?.items || [])
        this.drivers = list.map(item => ({
          id: item.id,
          name: item.driver_name || item.name || `驱动${item.id}`
        }))
      } catch (error) {
        console.error('加载驱动失败:', error)
        this.drivers = []
      }
    },
    getDriverName(driverId) {
      const hit = this.drivers.find(item => String(item.id) === String(driverId))
      return hit ? hit.name : '-'
    },
    async fetchVariables() {
      if (!this.deviceId) {
        console.warn('deviceId is null, skip loading')
        return
      }
      this.loading = true
      try {
        const res = await getDeviceVariables(this.deviceId, { page: 1, page_size: 9999 })
        const list = Array.isArray(res.data) ? res.data : (res.data?.items || [])
        this.variableList = list.map(item => this.normalizeVariable(item))
        this.applySearchAndPagination()
      } catch (error) {
        console.error('加载变量失败:', error)
        if (error.response?.status !== 404) {
          this.$message.error('加载变量失败')
        }
      } finally {
        this.loading = false
      }
    },
    applySearchAndPagination() {
      const keyword = this.searchForm.keyword.trim().toLowerCase()
      this.filteredList = this.variableList.filter(item => {
        const hitKeyword = !keyword || item.name.toLowerCase().includes(keyword) || item.registerAddress.toLowerCase().includes(keyword)
        const hitDriver = !this.searchForm.driverId || String(item.driverId) === String(this.searchForm.driverId)
        const hitVarType = !this.searchForm.variableType || item.variableType === this.searchForm.variableType
        const hitCycle = !this.searchForm.cycleCollect || item.cycleCollect === this.searchForm.cycleCollect
        return hitKeyword && hitDriver && hitVarType && hitCycle
      })
      this.total = this.filteredList.length
      const start = (this.currentPage - 1) * this.pageSize
      this.pageData = this.filteredList.slice(start, start + this.pageSize)
    },
    handleSelectionChange(selection) {
      this.selectedVars = selection
    },
    handleSearch() {
      this.currentPage = 1
      this.applySearchAndPagination()
    },
    resetSearch() {
      this.searchForm = {
        keyword: '',
        driverId: '',
        variableType: '',
        cycleCollect: ''
      }
      this.currentPage = 1
      this.applySearchAndPagination()
    },
    getDialogDefaultForm() {
      return {
        name: '',
        registerAddress: '',
        dataType: 'int16',
        registerType: 'holding',
        readWrite: 'read',
        cycleCollect: 'on',
        driverId: this.drivers[0]?.id || '',
        variableType: 'device'
      }
    },
    openCreateDialog() {
      this.dialogMode = 'create'
      this.editingId = null
      this.variableForm = this.getDialogDefaultForm()
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs.variableForm && this.$refs.variableForm.clearValidate()
      })
    },
    openEditDialog(row) {
      this.dialogMode = 'edit'
      this.editingId = row.id
      this.variableForm = {
        name: row.name,
        registerAddress: row.registerAddress,
        dataType: row.dataType,
        registerType: row.registerType,
        readWrite: row.readWrite,
        cycleCollect: row.cycleCollect,
        driverId: row.driverId,
        variableType: row.variableType
      }
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs.variableForm && this.$refs.variableForm.clearValidate()
      })
    },
    handleCopy(row) {
      this.dialogMode = 'create'
      this.editingId = null
      this.variableForm = {
        name: `${row.name}_copy`,
        registerAddress: row.registerAddress,
        dataType: row.dataType,
        registerType: row.registerType,
        readWrite: row.readWrite,
        cycleCollect: row.cycleCollect,
        driverId: row.driverId,
        variableType: row.variableType
      }
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs.variableForm && this.$refs.variableForm.clearValidate()
      })
    },
    buildPayload() {
      return {
        var_name: this.variableForm.name,
        name: this.variableForm.name,
        address: Number(this.variableForm.registerAddress),
        register_address: Number(this.variableForm.registerAddress),
        data_type: this.variableForm.dataType,
        register_type: this.variableForm.registerType,
        read_write: this.variableForm.readWrite,
        cycle_collect: this.variableForm.cycleCollect === 'on',
        collect_mode: this.variableForm.cycleCollect,
        driver_id: this.variableForm.driverId,
        variable_type: this.variableForm.variableType
      }
    },
    async handleSubmit() {
      if (!this.deviceId) return
      this.$refs.variableForm.validate(async valid => {
        if (!valid) return

        this.submitLoading = true
        try {
          const payload = this.buildPayload()
          if (this.dialogMode === 'create') {
            await createDeviceVariable(this.deviceId, payload)
            this.$message.success('变量创建成功')
          } else {
            await updateDeviceVariable(this.deviceId, this.editingId, payload)
            this.$message.success('变量更新成功')
          }
          this.dialogVisible = false
          await this.fetchVariables()
        } catch (error) {
          console.error('保存变量失败:', error)
          this.$message.error('保存失败，请检查参数后重试')
        } finally {
          this.submitLoading = false
        }
      })
    },
    resetDialog() {
      this.editingId = null
      this.submitLoading = false
      this.variableForm = this.getDialogDefaultForm()
    },
    async handleDelete(row) {
      try {
        await this.$confirm(`确认删除变量“${row.name}”吗？`, '提示', {
          type: 'warning'
        })
        await batchDeleteVariables(this.deviceId, [row.id])
        this.$message.success('删除成功')
        await this.fetchVariables()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除变量失败:', error)
          this.$message.error('删除失败')
        }
      }
    },
    async handleBatchDelete() {
      if (!this.selectedVars.length) return
      try {
        await this.$confirm(`确认删除选中的 ${this.selectedVars.length} 条变量吗？`, '提示', {
          type: 'warning'
        })
        const ids = this.selectedVars.map(item => item.id).filter(Boolean)
        if (!ids.length) {
          this.$message.warning('选中数据缺少ID，无法删除')
          return
        }
        await batchDeleteVariables(this.deviceId, ids)
        this.$message.success('批量删除成功')
        this.selectedVars = []
        await this.fetchVariables()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量删除失败:', error)
          this.$message.error('批量删除失败')
        }
      }
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.applySearchAndPagination()
    },
    handlePageChange(page) {
      this.currentPage = page
      this.applySearchAndPagination()
    },
    handleNext() {
      this.$emit('next')
    },
    goBack() {
      this.$router.back()
    },
    initWebSocket() {
      // 注意：这里连接的是你 Docker 部署的 Nginx 地址
      this.ws = new WebSocket('ws://127.0.0.1/api/v1/gateway/ws')

      this.ws.onmessage = (event) => {
        try {
          const incomingData = JSON.parse(event.data)
          
          // 1. 解构提取网关编号和具体的传感器数据
          const { gateway_sn, ...variableData } = incomingData

          // 2. 寻址拦截：只有发来的 SN 跟当前页面绑定的 SN 一致才处理
          if (gateway_sn === this.gatewaySn) {
            
            // 3. 动态映射与上下对齐
            // 遍历我们表格的底层数据源 variableList
            this.variableList.forEach(row => {
              // 策略 A：按“变量名称”匹配（假设后端发 {"温度1": 25}）
              if (variableData[row.name] !== undefined) {
                row.currentValue = variableData[row.name]
              }
              // 策略 B：按“寄存器地址”匹配（假设后端发 {"40001": 25.5}）
              else if (variableData[row.registerAddress] !== undefined) {
                row.currentValue = variableData[row.registerAddress]
              }
            })
            
            // 强制刷新当前页面的数据映射
            this.applySearchAndPagination()
          }
        } catch (error) {
          console.error("解析 WebSocket 数据失败:", error)
        }
      }

      this.ws.onerror = () => {
        console.error('网关实时数据通道连接失败')
      }
    }
  }
}
</script>

<style scoped>
.tips-alert {
  margin-bottom: 16px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
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

.danger-text {
  color: #f56c6c;
}

.stat-text {
  color: #606266;
}

.pagination-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-actions {
  margin-top: 20px;
}

.w-240 {
  width: 240px;
}

.w-180 {
  width: 180px;
}

.w-160 {
  width: 160px;
}

.w-140 {
  width: 140px;
}

.footer-actions {
  margin-top: 20px;
}

.variable-form {
  padding-right: 8px;
}
</style>
