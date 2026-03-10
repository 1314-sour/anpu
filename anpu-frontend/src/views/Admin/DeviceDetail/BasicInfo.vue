<template>
  <div class="basic-info-tab">
    <el-form :model="form" :rules="rules" ref="basicForm" label-width="110px" class="info-form">
      <!-- 选择图片 -->
      <el-form-item label="选择图片：">
        <el-upload
          class="image-uploader"
          :action="uploadUrl"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          :before-upload="beforeUpload"
          :headers="uploadHeaders">
          <img v-if="form.image_url" :src="form.image_url" class="device-image" />
          <div v-else class="upload-placeholder">
            <i class="el-icon-plus"></i>
          </div>
        </el-upload>
      </el-form-item>
      
      <!-- 设备名称 -->
      <el-form-item label="设备名称：" prop="name">
        <el-input v-model="form.name" placeholder="请输入设备名称"></el-input>
        <div class="error-tip" v-if="showNameError">请输入设备名称</div>
      </el-form-item>
      
      <!-- 所属分组 -->
      <el-form-item label="所属分组：">
        <el-select v-model="form.group_id" placeholder="请选择分组" style="width: 100%;">
          <el-option v-for="group in groupList" :key="group.id" :label="group.label" :value="group.id"></el-option>
        </el-select>
      </el-form-item>
      
      <!-- 详细地址 -->
      <el-form-item label="详细地址：">
        <div style="display: flex; gap: 10px;">
          <el-input v-model="form.address" placeholder="地址" style="flex: 1;"></el-input>
          <el-button type="primary" @click="handleMapLocation">地图</el-button>
        </div>
      </el-form-item>
      
      <!-- 经纬度 -->
      <el-form-item label="经纬度：">
        <div style="display: flex; gap: 10px;">
          <el-input v-model="form.longitude" placeholder="经度" style="flex: 1;"></el-input>
          <el-input v-model="form.latitude" placeholder="纬度" style="flex: 1;"></el-input>
        </div>
      </el-form-item>
      
      <!-- 是否分享 -->
      <el-form-item label="是否分享：">
        <el-radio-group v-model="form.coordinate_type">
          <el-radio label="是">是</el-radio>
          <el-radio label="否">否</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <!-- 顶部菜单栏 -->
      <el-form-item label="顶部菜单栏：">
        <el-radio-group v-model="form.top_order_unit">
          <el-radio label="默示">显示</el-radio>
          <el-radio label="隐藏">隐藏</el-radio>
          <el-tooltip content="说明信息" placement="top">
            <i class="el-icon-question" style="margin-left: 5px; cursor: pointer;"></i>
          </el-tooltip>
        </el-radio-group>
      </el-form-item>
      
      <!-- 缺错值 -->
      <el-form-item label="缺错值：">
        <el-radio-group v-model="form.default_value_type">
          <el-radio label="自定义">自定义</el-radio>
          <el-radio label="集后采集值">集后采集值</el-radio>
          <el-tooltip content="说明信息" placement="top">
            <i class="el-icon-question" style="margin-left: 5px; cursor: pointer;"></i>
          </el-tooltip>
        </el-radio-group>
        <el-input v-model="form.default_value" placeholder="0" style="margin-top: 10px;"></el-input>
      </el-form-item>
      
      <!-- 隐藏字段 -->
      <div v-show="showMoreFields">
        <!-- 设备编号 -->
        <el-form-item label="设备编号：">
          <el-input v-model="form.device_number" placeholder="请输入设备编号"></el-input>
        </el-form-item>
        
        <!-- 出厂日期 -->
        <el-form-item label="出厂日期：">
          <el-date-picker
            v-model="form.manufacture_date"
            type="date"
            placeholder="请选择出厂日期"
            style="width: 100%;"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd">
          </el-date-picker>
        </el-form-item>
        
        <!-- 安装日期 -->
        <el-form-item label="安装日期：">
          <el-date-picker
            v-model="form.install_date"
            type="date"
            placeholder="请选择安装日期"
            style="width: 100%;"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd">
          </el-date-picker>
        </el-form-item>
        
        <!-- 保修时长 -->
        <el-form-item label="保修时长：">
          <div style="display: flex; gap: 10px;">
            <el-input v-model="form.warranty_years" placeholder="请输入" style="flex: 1;"></el-input>
            <el-select v-model="form.warranty_unit" style="width: 100px;">
              <el-option label="年" value="年"></el-option>
              <el-option label="月" value="月"></el-option>
            </el-select>
          </div>
        </el-form-item>
        
        <!-- 生产厂商 -->
        <el-form-item label="生产厂商：">
          <el-input v-model="form.manufacturer" placeholder="请输入生产厂商"></el-input>
        </el-form-item>
        
        <!-- 排序号 -->
        <el-form-item label="排序号：">
          <el-input v-model="form.sort" placeholder="排序标识，支持字段数字、数字最大设备首前"></el-input>
        </el-form-item>
        
        <!-- 备注 -->
        <el-form-item label="备注：">
          <el-input v-model="form.remark" placeholder="备注"></el-input>
        </el-form-item>
      </div>
      
      <!-- 隐藏更多字段 -->
      <el-form-item>
        <el-link type="primary" :underline="false" @click="toggleMoreFields">
          <i :class="showMoreFields ? 'el-icon-caret-top' : 'el-icon-caret-bottom'"></i>
          {{ showMoreFields ? '隐藏更多字段' : '显示更多字段' }}
        </el-link>
      </el-form-item>
      
      <!-- 保存按钮 -->
      <el-form-item>
        <el-button type="primary" @click="saveAndNext" :loading="loading">保存并下一步</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 右侧信息栏 -->
    <div class="info-sidebar">
      <div class="info-card">
        <div class="card-title">如何新增设备</div>
        <div class="card-content">
          <p>1. 完成设备基本信息，包括设备名称、所属分组、设备位置和其他信息等。</p>
          <p>2. 填写SN编号认证后码定网关。</p>
          <p>3. 创建驱动，支持多种PLC或传，可连接RS232、RS485、LAN等端口与PLC进行通讯。</p>
          <p>4. 添加变量，设置报表，这些输入等形式进行批量操作。</p>
          <p>5. 添加历史报表，可创建多个报表，不同报表对应设备不同的存储方式。</p>
          <p>6. 编写脚本，当某些任务需要机器中间变更时，可以用脚本代码进行解决。</p>
          <p style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #f0f0f0;">
            以上步骤，也可通过模板方式快速进行验证。变量、报表、脚本配置信息快速同步至网关。节省您的时间和精力。
          </p>
        </div>
      </div>
      
      <div class="info-card">
        <div class="card-title">为什么部分功能无法使用</div>
        <div class="card-content">
          <p>由于性能原因，EG10系列产品及CLC系控制器对部分的功能暂不支持，包括部分通讯端口。部分协议。历史报表存储方式。不支持脚本功能。如需要使用平台完整功能，可以向商家人员了解其他产品详情。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { createDevice, updateDevice, getGroups, getDeviceDetail, checkDeviceName } from '@/api/device'
import { API_BASE_URL } from '@/api/request'

export default {
  name: 'BasicInfo',
  props: {
    deviceId: {
      type: Number,
      default: null
    },
    mode: {
      type: String,
      default: 'edit'
    }
  },
  data() {
   return {
      loading: false,
      showMoreFields: false,
      showNameError: false,
      groupList: [],
      uploadUrl: `${API_BASE_URL}/api/v1/upload/image`,
      uploadHeaders: {
        'Authorization': 'Bearer ' + localStorage.getItem('token')
      },
      form: {
        image_url: '',
        name: '',
        sn: '',
        status: 'offline',
        group_id: null,
        address: '',
        latitude: '',
        longitude: '',
        coordinate_type: '东',
        top_order_unit: '默示',
        default_value_type: '自定义',
        default_value: '0',
        device_number: '',
        manufacture_date: '',
        install_date: '',
        warranty_years: '',
        warranty_unit: '年',
        manufacturer: '',
        sort: '',
        remark: '',
        iccid: ''
      },
      rules: {
        name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.fetchGroupList()
    if (this.mode === 'edit' && this.deviceId) {
      this.loadDeviceData()
    }
  },
  methods: {
    async fetchGroupList() {
      try {
        const res = await getGroups()
        this.groupList = res.data || []
      } catch (error) {
        console.error('加载分组失败:', error)
      }
    },
    
    loadDeviceData() {
      getDeviceDetail(this.deviceId).then(res => {
        const data = res.data
        this.form = {
          image_url: data.image_url || '',
          name: data.name || '',
          sn: data.sn || '',
          status: data.status || 'offline',
          group_id: data.group_id || null,
          address: data.address || '',
          latitude: data.latitude || '',
          longitude: data.longitude || '',
          coordinate_type: data.coordinate_type || '东',
          top_order_unit: data.top_order_unit || '默示',
          default_value_type: data.default_value_type || '自定义',
          default_value: data.default_value || '0',
          device_number: data.device_number || '',
          manufacture_date: data.manufacture_date || '',
          install_date: data.install_date || '',
          warranty_years: data.warranty_years || '',
          warranty_unit: data.warranty_unit || '年',
          manufacturer: data.manufacturer || '',
          sort: data.sort || '',
          remark: data.remark || '',
          iccid: data.iccid || ''
        }
      }).catch(error => {
        console.error('加载设备数据失败:', error)
        this.$message.error('加载设备数据失败')
      })
    },
    
    async saveAndNext() {
      this.showNameError = false
      
      this.$refs.basicForm.validate(async (valid) => {
        if (!valid) {
          this.showNameError = !this.form.name
          return
        }
        
        this.loading = true
        try {
          // 先检查设备名称是否已存在
          const excludeId = this.mode === 'edit' ? this.deviceId : null
          const checkRes = await checkDeviceName(this.form.name, excludeId)
          if (checkRes.data.exists) {
            this.$message.error('该名称已存在，请勿重复添加')
            this.loading = false
            return
          }
          
          let currentDeviceId = this.deviceId
          
          // 准备要提交的数据，确保数据类型正确
          const submitData = {
            ...this.form,
            latitude: this.form.latitude ? parseFloat(this.form.latitude) : null,
            longitude: this.form.longitude ? parseFloat(this.form.longitude) : null,
            sort: this.form.sort ? parseInt(this.form.sort) : 0,
            // 日期字段：空字符串转为null
            manufacture_date: this.form.manufacture_date || null,
            install_date: this.form.install_date || null
          }
          
          if (this.mode === 'create') {
            console.log('提交数据:', submitData)
            const deviceRes = await createDevice(submitData)
            currentDeviceId = deviceRes.data.id
            this.$emit('device-created', currentDeviceId)
          } else {
            await updateDevice(this.deviceId, submitData)
          }
          
          this.$message.success('保存成功')
          this.$emit('next')
        } catch (error) {
          console.error('保存失败:', error)
          console.error('错误详情:', error.response?.data)
          this.$message.error(error.response?.data?.detail || '保存失败')
        } finally {
          this.loading = false
        }
      })
    },
    
    toggleMoreFields() {
      this.showMoreFields = !this.showMoreFields
    },
    
    beforeUpload(file) {
      const isImage = file.type.startsWith('image/')
      const isLt2M = file.size / 1024 / 1024 < 2
      
      if (!isImage) {
        this.$message.error('只能上传图片文件！')
        return false
      }
      if (!isLt2M) {
        this.$message.error('图片大小不能超过 2MB！')
        return false
      }
      return true
    },
    
    handleUploadSuccess(response) {
      if (response.code === 200) {
        this.form.image_url = response.data.url
        this.$message.success('图片上传成功')
      } else {
        this.$message.error(response.message || '图片上传失败')
      }
    },
    
    handleMapLocation() {
      this.$message.info('地图定位功能待实现')
    },
    
    goBack() {
      this.$router.back()
    }
  }
}
</script>

<style scoped>
.basic-info-tab {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: #f0f2f5;
  min-height: calc(100vh - 200px);
}

.info-form {
  flex: 6;
  background: white;
  padding: 30px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.error-tip {
  color: #f56c6c;
  font-size: 12px;
  line-height: 1;
  padding-top: 4px;
}

.image-uploader {
  display: inline-block;
}

.device-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  display: block;
}

.upload-placeholder {
  width: 120px;
  height: 120px;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.upload-placeholder:hover {
  border-color: #409eff;
}

.upload-placeholder i {
  font-size: 32px;
  color: #8c939d;
}

.info-sidebar {
  flex: 4;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-card {
  background: #fff;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.card-title {
  background: linear-gradient(90deg, #fff7e6 0%, #fffbf0 100%);
  color: #fa8c16;
  padding: 12px 15px;
  font-weight: bold;
  font-size: 14px;
  border-left: 3px solid #fa8c16;
}

.card-content {
  padding: 15px;
  font-size: 13px;
  line-height: 1.8;
  color: #666;
}

.card-content p {
  margin: 8px 0;
}

/* Element UI 表单样式调整 */
::v-deep .el-form-item {
  margin-bottom: 22px;
}

::v-deep .el-form-item__label {
  color: #606266;
  font-weight: normal;
}

::v-deep .el-input__inner,
::v-deep .el-textarea__inner {
  border-radius: 4px;
}

::v-deep .el-date-editor.el-input {
  width: 100%;
}
</style>
