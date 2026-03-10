<template>
  <div class="drivers-manage-tab">
    <!-- 左侧绑定网关 -->
    <div class="bind-gateway-section">
      <div class="section-title">绑定网关</div>
      <div class="warning-tip">
        <i class="el-icon-warning"></i>
        温馨提示：您还没有绑定网关，绑定网关后可添加驱动
      </div>
      
      <el-form :model="gatewayForm" :rules="gatewayRules" ref="gatewayForm" label-width="100px" class="gateway-form">
        <el-form-item label="SN编号：" prop="sn">
          <el-input v-model="gatewayForm.sn" placeholder="请输入SN编号"></el-input>
        </el-form-item>
        
        <el-form-item label="验证码：" prop="code">
          <el-input v-model="gatewayForm.code" placeholder="请输入验证码"></el-input>
        </el-form-item>
        
        <el-form-item label="绑定模板：">
          <el-radio-group v-model="gatewayForm.useTemplate">
            <el-radio :label="false">是</el-radio>
            <el-radio :label="true">否</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="模板：" v-if="gatewayForm.useTemplate === false">
          <div style="display: flex; gap: 10px;">
            <el-input v-model="gatewayForm.template" placeholder="请选择" readonly></el-input>
            <el-button type="primary" @click="handleSelectTemplate">选择</el-button>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSaveGateway">保存并下一步</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 右侧帮助信息 -->
    <div class="help-section">
      <div class="help-card">
        <div class="help-title">网关的SN编号和验证码去哪里获取呢？</div>
        <div class="help-content">
          <p>EQ设备网关的SN编号和验证码，一般位于网关盒子顶端的标签中，SIM卡槽在上面（不同设备型号位置会略有差异）</p>
          <div class="gateway-image">
            <img src="@/assets/gateway-sn.svg" alt="网关SN" />
          </div>
          <p>每台设备自前仅支持绑定一台网关，如果当前网关大已被其他设备绑定，请先去其他设备中移除网关后再进行绑定</p>
          <p>如果您绑定网关过程中出现异常的情况，请联系您的售后服务人员或客服人员为您处理</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DriversManage',
  props: {
    deviceId: Number,
    mode: String
  },
  data() {
    return {
      gatewayForm: {
        sn: '',
        code: '',
        useTemplate: true,
        template: ''
      },
      gatewayRules: {
        sn: [{ required: true, message: '请输入SN编号', trigger: 'blur' }],
        code: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
      }
    }
  },
  methods: {
    handleSelectTemplate() {
      this.$message.info('显示功能待开发')
    },
    handleSaveGateway() {
      this.$refs.gatewayForm.validate((valid) => {
        if (valid) {
          // TODO: 调用API保存网关信息
          this.$message.success('保存成功')
          this.$emit('next')
        }
      })
    }
  }
}
</script>

<style scoped>
.drivers-manage-tab {
  display: flex;
  gap: 30px;
  padding: 20px;
}

.bind-gateway-section {
  flex: 1;
  max-width: 600px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 15px;
}

.warning-tip {
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
  padding: 12px 15px;
  border-radius: 4px;
  color: #f56c6c;
  margin-bottom: 25px;
  font-size: 14px;
}

.warning-tip i {
  margin-right: 8px;
}

.gateway-form {
  margin-top: 20px;
}

.help-section {
  flex: 1;
  max-width: 500px;
}

.help-card {
  background-color: #fffbf0;
  border: 1px solid #faecd8;
  border-radius: 4px;
  padding: 20px;
}

.help-title {
  color: #e6a23c;
  font-size: 15px;
  font-weight: bold;
  margin-bottom: 15px;
}

.help-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.help-content p {
  margin: 10px 0;
}

.gateway-image {
  margin: 20px 0;
  text-align: center;
}

.gateway-image img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}
</style>
