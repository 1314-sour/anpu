<template>
  <div class="device-list-page">
    <!-- 搜索和操作栏 -->
    <div class="filter-container">
      <el-input v-model="searchQuery" placeholder="名称、SN编号、地址、ICCID、备注" style="width: 300px; margin-right: 10px;" size="small"></el-input>
      <el-select v-model="statusFilter" placeholder="全部状态" style="width: 120px; margin-right: 10px;" size="small">
        <el-option label="全部状态" value=""></el-option>
        <el-option label="在线" value="online"></el-option>
        <el-option label="离线" value="offline"></el-option>
        
      </el-select>
      <el-select v-model="groupFilter" placeholder="全部分组" style="width: 120px; margin-right: 10px;" size="small">
        <el-option label="全部分组" value=""></el-option>
        <el-option v-for="group in groupList" :key="group.id" :label="group.label" :value="group.id"></el-option>
        <el-option label="未分组" :value="-1"></el-option>
      </el-select>
      <el-button type="primary" icon="el-icon-search" size="small" @click="handleSearch">搜索</el-button>
      <el-button type="text" size="small" @click="advancedSearchVisible = true">高级搜索</el-button>
      <el-checkbox v-model="autoRefresh" style="margin-left: 10px;">由我创建</el-checkbox>

      <div class="right-actions" style="float: right;">
        <el-button type="primary" plain size="small" @click="openImportDialog">导入设备</el-button>
        <el-button type="primary" icon="el-icon-plus" size="small" @click="handleAdd">新增</el-button>
      </div>
    </div>

    <div class="table-header-actions" style="margin: 15px 0; display: flex; justify-content: space-between; align-items: center;">
      <span>设备列表 ({{ total }})</span>
      <div>
        <el-button type="text" icon="el-icon-download">导出设备信息</el-button>
        <span style="margin: 0 10px; color: #dcdfe6;">|</span>
        <el-button type="text" icon="el-icon-s-grid">显示列</el-button>
      </div>
    </div>

    <!-- 设备列表表格 -->
    <el-table :data="deviceList" style="width: 100%" :header-cell-style="{background:'#f5f7fa',color:'#606266'}">
      <el-table-column prop="name" label="设备名称" min-width="150">
        <template slot-scope="scope">
          <span :class="{'text-warning': scope.row.status === 'offline'}">{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="sn" label="网关SN编号" width="150"></el-table-column>
      <el-table-column prop="status" label="网关状态" width="100">
        <template slot-scope="scope">
          <span :class="scope.row.status === 'online' ? 'status-online' : 'status-offline'">
            {{ scope.row.status === 'online' ? '在线' : '离线' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="group" label="所属分组" width="120"></el-table-column>
      <el-table-column prop="address" label="所在地" min-width="200"></el-table-column>
      <el-table-column prop="creator" label="创建人" width="100"></el-table-column>
      <el-table-column prop="remark" label="备注" min-width="100"></el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template slot-scope="scope">
          <el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <span class="separator">|</span>
          <el-button type="text" size="small" @click="handleAuth(scope.row)">授权</el-button>
          <span class="separator">|</span>
          <el-button type="text" size="small" @click="handleCopy(scope.row)">复制</el-button>
          <span class="separator">|</span>
          <el-button type="text" size="small">导出设备</el-button>
          <span class="separator">|</span>
          <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, scope.row)">
            <span class="el-dropdown-link">
              <i class="el-icon-more" style="cursor: pointer; color: #409EFF;"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="delete">删除</el-dropdown-item>
              <el-dropdown-item command="detail">详情</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container" style="margin-top: 20px; text-align: right;">
      <span style="margin-right: 10px; color: #606266;">共有{{ total }}条</span>
      <el-pagination
        background
        layout="prev, pager, next, sizes, jumper"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange">
      </el-pagination>
    </div>

    <!-- 导入设备弹窗 -->
    <el-dialog title="导入设备" :visible.sync="importDialogVisible" width="600px">
      <el-form :model="importForm" :rules="importRules" ref="importForm" label-width="110px">
        <el-form-item label="设备名称：" prop="name">
          <el-input v-model="importForm.name" placeholder="请输入设备名称"></el-input>
        </el-form-item>
        <el-form-item label="网关SN编号：" prop="sn">
          <el-input v-model="importForm.sn" placeholder="请输入网关SN编号"></el-input>
        </el-form-item>
        <el-form-item label="网关验证码：" prop="code">
          <el-input v-model="importForm.code" placeholder="请输入eg.网关验证码"></el-input>
        </el-form-item>
        <el-form-item label="配置文件：" prop="file">
          <div style="display: flex;">
            <el-input v-model="importForm.fileName" placeholder="请选择文件" readonly style="flex: 1; margin-right: 10px;"></el-input>
            <input type="file" ref="fileInput" @change="handleFileChange" style="display: none;">
            <el-button type="primary" @click="$refs.fileInput.click()">选择文件</el-button>
          </div>
        </el-form-item>
        <el-form-item label="排序号：" prop="sort">
          <el-input v-model="importForm.sort" placeholder="排序标识，支持正整数，数字越大设备越靠前"></el-input>
        </el-form-item>
      </el-form>

      <div class="import-tip">
        <div class="tip-title">*温馨提示：</div>
        <p>1.导入设备功能可快速将您已创建好的设备配置信息导入到一台新设备中，包括网关、驱动配置，变量配置，组态页面，报警配置和历史报表配置</p>
        <p>2.您需要填写新设备所绑定的网关SN编号和校验码，请确保设备网关处于在线状态，否则将无法导入成功</p>
        <p>3.导入设备过程中，请勿将设备断电、重启或断开网络，否则设备信息将无法导入成功</p>
        <p>4.只能导入相同系列的网关信息，如果网关系列不同，则无法导入成功</p>
        <p class="text-danger">5.导入设备后，网关已存储的历史报表、报警记录会被清空，请谨慎操作</p>
      </div>

      <span slot="footer" class="dialog-footer">
        <el-button @click="importDialogVisible = false">关 闭</el-button>
        <el-button type="primary" @click="submitImport">确 定</el-button>
      </span>
    </el-dialog>

    <!-- 设备编辑/新增弹窗 -->
    <el-dialog :title="deviceDialogTitle" :visible.sync="deviceDialogVisible" width="600px">
      <el-form :model="deviceForm" :rules="deviceRules" ref="deviceForm" label-width="110px">
        <el-form-item label="设备名称：" prop="name">
          <el-input v-model="deviceForm.name" placeholder="请输入设备名称"></el-input>
        </el-form-item>
        <el-form-item label="网关SN：" prop="sn">
          <el-input v-model="deviceForm.sn" placeholder="请输入网关SN编号" :disabled="!!deviceForm.id"></el-input>
        </el-form-item>
        <el-form-item label="状态：">
          <el-select v-model="deviceForm.status" style="width: 100%;">
            <el-option label="在线" value="online"></el-option>
            <el-option label="离线" value="offline"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="所属分组：">
          <el-select v-model="deviceForm.group_id" placeholder="请选择" clearable style="width: 100%;">
            <el-option v-for="group in groupList" :key="group.id" :label="group.label" :value="group.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="所在地：">
          <el-input v-model="deviceForm.address" placeholder="请输入地址"></el-input>
        </el-form-item>
        <el-form-item label="ICCID：">
          <el-input v-model="deviceForm.iccid" placeholder="请输入ICCID"></el-input>
        </el-form-item>
        <el-form-item label="排序号：">
          <el-input v-model.number="deviceForm.sort" placeholder="数字越大越靠前" type="number"></el-input>
        </el-form-item>
        <el-form-item label="备注：">
          <el-input v-model="deviceForm.remark" type="textarea" :rows="3" placeholder="请输入备注"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deviceDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitDeviceForm">确 定</el-button>
      </span>
    </el-dialog>
    
    <!-- 高级搜索弹窗 -->
    <el-dialog title="高级搜索" :visible.sync="advancedSearchVisible" width="800px" :close-on-click-modal="false">
      <el-form :model="advancedSearchForm" label-width="100px" class="advanced-search-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生产厂商：">
              <el-select v-model="advancedSearchForm.manufacturer" placeholder="请选择" clearable style="width: 100%;">
                <el-option label="安普" value="安普"></el-option>
                <el-option label="其他" value="其他"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备编号：">
              <el-input v-model="advancedSearchForm.device_number" placeholder="请输入"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分组：">
              <el-select v-model="advancedSearchForm.group_id" placeholder="全部状态" clearable style="width: 100%;">
                <el-option label="全部状态" value=""></el-option>
                <el-option v-for="group in groupList" :key="group.id" :label="group.label" :value="group.id"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="创建人：">
              <el-input v-model="advancedSearchForm.creator" placeholder="请输入"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="保修截止：">
              <div style="display: flex; gap: 10px; align-items: center;">
                <el-input v-model="advancedSearchForm.warranty_start" placeholder="请输入" style="flex: 1;"></el-input>
                <el-select v-model="advancedSearchForm.warranty_start_unit" style="width: 80px;">
                  <el-option label="年" value="年"></el-option>
                  <el-option label="月" value="月"></el-option>
                </el-select>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <div style="display: flex; gap: 10px; align-items: center; padding-top: 40px;">
              <span>—</span>
              <el-input v-model="advancedSearchForm.warranty_end" placeholder="请输入" style="flex: 1;"></el-input>
              <el-select v-model="advancedSearchForm.warranty_end_unit" style="width: 80px;">
                <el-option label="年" value="年"></el-option>
                <el-option label="月" value="月"></el-option>
              </el-select>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出厂日期：">
              <el-date-picker
                v-model="advancedSearchForm.manufacture_start"
                type="date"
                placeholder="开始日期"
                style="width: 100%;"
                format="yyyy-MM-dd"
                value-format="yyyy-MM-dd">
              </el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <div style="display: flex; gap: 10px; align-items: center; padding-top: 40px;">
              <span>—</span>
              <el-date-picker
                v-model="advancedSearchForm.manufacture_end"
                type="date"
                placeholder="结束日期"
                style="width: 100%;"
                format="yyyy-MM-dd"
                value-format="yyyy-MM-dd">
              </el-date-picker>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="安装日期：">
              <el-date-picker
                v-model="advancedSearchForm.install_start"
                type="date"
                placeholder="开始日期"
                style="width: 100%;"
                format="yyyy-MM-dd"
                value-format="yyyy-MM-dd">
              </el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <div style="display: flex; gap: 10px; align-items: center; padding-top: 40px;">
              <span>—</span>
              <el-date-picker
                v-model="advancedSearchForm.install_end"
                type="date"
                placeholder="结束日期"
                style="width: 100%;"
                format="yyyy-MM-dd"
                value-format="yyyy-MM-dd">
              </el-date-picker>
            </div>
          </el-col>
        </el-row>
        
        <el-form-item label="模板名称：">
          <el-input v-model="advancedSearchForm.template_name" placeholder="请输入"></el-input>
        </el-form-item>
      </el-form>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="advancedSearchVisible = false">关 闭</el-button>
        <el-button type="primary" @click="handleAdvancedSearch">确 定</el-button>
      </span>
    </el-dialog>
    
    <!-- 复制设备弹窗 -->
    <copy-device-dialog
      :visible.sync="copyDialogVisible"
      :device-data="currentDevice"
      @submit="handleCopySubmit">
    </copy-device-dialog>
    
    <!-- 账号授权管理弹窗 -->
    <auth-manage-dialog
      :visible.sync="authDialogVisible"
      :device-id="currentDevice.id">
    </auth-manage-dialog>
  </div>
</template>

<script>
import { getDevices, createDevice, updateDevice, deleteDevice, getGroups } from '@/api/device'
import CopyDeviceDialog from '@/components/CopyDeviceDialog.vue'
import AuthManageDialog from '@/components/AuthManageDialog.vue'

export default {
  name: 'DeviceList',
  components: {
    CopyDeviceDialog,
    AuthManageDialog
  },
  data() {
    return {
      searchQuery: '',
      statusFilter: '',
      groupFilter: '',
      autoRefresh: false,
      total: 0,
      pageSize: 10,
      currentPage: 1,
      deviceList: [],
      groupList: [],
      loading: false,
      
      // 复制设备弹窗
      copyDialogVisible: false,
      
      // 账号授权管理弹窗
      authDialogVisible: false,
      
      // 当前操作的设备
      currentDevice: {},
      
      // 导入设备弹窗
      importDialogVisible: false,
      importForm: {
        name: '',
        sn: '',
        code: '',
        file: null,
        fileName: '',
        sort: ''
      },
      importRules: {
        name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
        sn: [{ required: true, message: '请输入网关SN编号', trigger: 'blur' }],
        code: [{ required: true, message: '请输入网关验证码', trigger: 'blur' }],
        file: [{ required: true, message: '请选择配置文件', trigger: 'change' }]
      },
      
      // 设备编辑/新增弹窗
      deviceDialogVisible: false,
      deviceDialogTitle: '新增设备',
      deviceForm: {
        id: null,
        name: '',
        sn: '',
        status: 'offline',
        group_id: null,
        address: '',
        remark: '',
        iccid: '',
        sort: 0
      },
      deviceRules: {
        name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
        sn: [{ required: true, message: '请输入网关SN编号', trigger: 'blur' }]
      },
      
      // 高级搜索弹窗
      advancedSearchVisible: false,
      advancedSearchForm: {
        manufacturer: '',
        device_number: '',
        group_id: '',
        creator: '',
        warranty_start: '',
        warranty_start_unit: '年',
        warranty_end: '',
        warranty_end_unit: '年',
        manufacture_start: '',
        manufacture_end: '',
        install_start: '',
        install_end: '',
        template_name: ''
      }
    }
  },
  mounted() {
    this.fetchDeviceList()
    this.fetchGroupList()
  },
  methods: {
    async fetchDeviceList() {
      this.loading = true
      try {
        const res = await getDevices({
          search: this.searchQuery,
          status: this.statusFilter,
          group_id: this.groupFilter || undefined,
          page: this.currentPage,
          page_size: this.pageSize
        })
        this.deviceList = res.data.list || []
        this.total = res.data.total || 0
      } catch (error) {
        console.error('加载设备失败:', error)
        this.$message.error('加载设备失败')
      } finally {
        this.loading = false
      }
    },
    async fetchGroupList() {
      try {
        const res = await getGroups()
        this.groupList = res.data || []
      } catch (error) {
        console.error('加载分组失败:', error)
      }
    },
    handleSearch() {
      this.currentPage = 1
      this.fetchDeviceList()
    },
    handleAdd() {
      // 跳转到设备详情页面（新增模式）
      this.$router.push({
        path: '/admin/device-detail',
        query: { mode: 'create' }
      })
    },
    handleEdit(row) {
      // 跳转到设备详情页面（编辑模式）
      this.$router.push({
        path: '/admin/device-detail',
        query: { id: row.id, mode: 'edit' }
      })
    },
    async submitDeviceForm() {
      this.$refs.deviceForm.validate(async (valid) => {
        if (valid) {
          try {
            if (this.deviceForm.id) {
              await updateDevice(this.deviceForm.id, this.deviceForm)
              this.$message.success('更新成功')
            } else {
              await createDevice(this.deviceForm)
              this.$message.success('创建成功')
            }
            this.deviceDialogVisible = false
            this.fetchDeviceList()
          } catch (error) {
            console.error('保存设备失败:', error)
            this.$message.error(error.response?.data?.detail || '保存失败')
          }
        }
      })
    },
    handleCommand(command, row) {
      if (command === 'delete') {
        this.handleDelete(row)
      } else if (command === 'detail') {
        this.$message.info('详情功能待实现')
      }
    },
    handleDelete(row) {
      this.$confirm(`确定要删除设备 "${row.name}" 吗?`, '提示', {
        type: 'warning'
      }).then(async () => {
        try {
          await deleteDevice(row.id)
          this.$message.success('删除成功')
          this.fetchDeviceList()
        } catch (error) {
          console.error('删除失败:', error)
          this.$message.error('删除失败')
        }
      }).catch(() => {})
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.fetchDeviceList()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchDeviceList()
    },
    openImportDialog() {
      this.importDialogVisible = true;
      this.importForm = { name: '', sn: '', code: '', file: null, fileName: '', sort: '' };
      this.$nextTick(() => {
        this.$refs.importForm.clearValidate();
      });
    },
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.importForm.file = file;
        this.importForm.fileName = file.name;
        this.$refs.importForm.clearValidate('file');
      }
    },
    submitImport() {
      this.$refs.importForm.validate((valid) => {
        if (valid) {
          const loading = this.$loading({
            lock: true,
            text: '正在导入设备...',
            spinner: 'el-icon-loading',
            background: 'rgba(0, 0, 0, 0.7)'
          })
          
          setTimeout(() => {
            loading.close()
            this.$message.success('设备导入成功')
            this.importDialogVisible = false
            this.fetchDeviceList()
          }, 1500)
        }
      })
    },
    
    handleAdvancedSearch() {
      // 应用高级搜索条件
      console.log('高级搜索条件:', this.advancedSearchForm)
      this.$message.success('高级搜索功能待实现')
      this.advancedSearchVisible = false
      // TODO: 根据高级搜索条件调用API
      // this.fetchDeviceList()
    },
    
    // 复制设备
    handleCopy(row) {
      this.currentDevice = { ...row }
      this.copyDialogVisible = true
    },
    
    // 处理复制设备提交
    handleCopySubmit(copyData) {
      console.log('复制设备数据:', copyData)
      // TODO: 调用复制设备的API
      // 这里可以调用后端API来执行复制操作
      this.$message.success('设备复制成功')
      this.fetchDeviceList()
    },
    
    // 账号授权管理
    handleAuth(row) {
      this.currentDevice = { ...row }
      this.authDialogVisible = true
    }
  }
}
</script>

<style scoped>
.status-online {
  color: #67c23a;
}
.status-offline {
  color: #909399;
}
.text-warning {
  color: #e6a23c;
}
.text-danger {
  color: #F56C6C;
}
.separator {
  margin: 0 5px;
  color: #dcdfe6;
}

.import-tip {
  background-color: #fdf6ec;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #faecd8;
  margin-top: 20px;
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.tip-title {
  color: #e6a23c;
  font-weight: bold;
  margin-bottom: 5px;
}
</style>
