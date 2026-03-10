<template>
  <el-dialog
    title="复制设备"
    :visible.sync="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose">
    <el-form :model="form" :rules="rules" ref="copyForm" label-width="140px">
      <el-form-item label="原设备名称：">
        <el-input v-model="originalDevice.name" disabled></el-input>
      </el-form-item>
      
      <el-form-item label="原设备网关SN编号：">
        <el-input v-model="originalDevice.sn" disabled></el-input>
      </el-form-item>
      
      <el-form-item label="新设备名称：" prop="name">
        <el-input v-model="form.name" placeholder="请输入新的设备名称"></el-input>
      </el-form-item>
      
      <el-form-item label="新设备网关SN编号：" prop="sn">
        <el-input v-model="form.sn" placeholder="请输入新设备网关SN编号"></el-input>
      </el-form-item>
      
      <el-form-item label="新设备网关验证码：" prop="verifyCode">
        <el-input v-model="form.verifyCode" placeholder="请输入新设备网关验证码"></el-input>
      </el-form-item>
      
      <el-form-item label="新设备排序号：">
        <el-input 
          v-model.number="form.sort" 
          placeholder="排序标识，支持正整数，数字越大设备越靠前"
          type="number">
        </el-input>
      </el-form-item>
    </el-form>
    
    <!-- 温馨提示 -->
    <div class="warm-tips">
      <div class="tips-title">*温馨提示：</div>
      <div class="tips-content">
        <p>1.复制设备功能即可连接您已创建好的设备配置信息复制到一台新设备中，包括网关配置、驱动配置、变量配置、组态页面、报警配置和历史报表配置</p>
        <p>2.您需要提供新设备所拥有的网关SN编号和验证码，请确保新设备网关处于在线状态，否则将无法复制成功</p>
        <p>3.复制设备过程中，请勿将设备离线，重启或断开网络，否则设备信息将无法复制成功</p>
        <p>4.只能复制相同系列的网关信息，如果网关系列不同，则无法复制成功</p>
      </div>
    </div>
    
    <span slot="footer" class="dialog-footer">
      <el-button @click="handleClose">关 闭</el-button>
      <el-button type="primary" @click="handleSubmit">确 定</el-button>
    </span>
  </el-dialog>
</template>

<script>
export default {
  name: 'CopyDeviceDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    deviceData: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      form: {
        name: '',
        sn: '',
        verifyCode: '',
        sort: ''
      },
      rules: {
        name: [
          { required: true, message: '请输入新设备名称', trigger: 'blur' }
        ],
        sn: [
          { required: true, message: '请输入新设备网关SN编号', trigger: 'blur' }
        ],
        verifyCode: [
          { required: true, message: '请输入新设备网关验证码', trigger: 'blur' }
        ]
      }
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
    },
    originalDevice() {
      return {
        name: this.deviceData.name || '',
        sn: this.deviceData.sn || ''
      }
    }
  },
  methods: {
    handleClose() {
      this.dialogVisible = false
      this.resetForm()
    },
    handleSubmit() {
      this.$refs.copyForm.validate((valid) => {
        if (valid) {
          // 这里调用复制设备的API
          const copyData = {
            originalDeviceId: this.deviceData.id,
            ...this.form
          }
          
          // 触发提交事件，让父组件处理
          this.$emit('submit', copyData)
          
          // 提示用户
          this.$message.success('设备复制成功')
          this.handleClose()
        }
      })
    },
    resetForm() {
      this.$refs.copyForm && this.$refs.copyForm.resetFields()
      this.form = {
        name: '',
        sn: '',
        verifyCode: '',
        sort: ''
      }
    }
  },
  watch: {
    visible(val) {
      if (!val) {
        this.resetForm()
      }
    }
  }
}
</script>

<style scoped>
.warm-tips {
  background-color: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 20px;
}

.tips-title {
  color: #faad14;
  font-weight: bold;
  margin-bottom: 10px;
}

.tips-content p {
  margin: 8px 0;
  line-height: 1.6;
  color: #666;
  font-size: 13px;
}

::v-deep .el-input.is-disabled .el-input__inner {
  background-color: #f5f7fa;
  color: #c0c4cc;
}
</style>
