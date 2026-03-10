<template>
  <div class="page-content">
    <div class="page-header">系统设置</div>
    <div class="page-body">
      <div class="setting-section">
        <div class="section-title">接收消息类型</div>
        <div class="section-content">
          <el-checkbox-group v-model="messageTypes">
            <el-checkbox label="保留消息"></el-checkbox>
            <el-checkbox label="工单消息"></el-checkbox>
            <el-checkbox label="到期提醒"></el-checkbox>
            <el-checkbox label="系统公告"></el-checkbox>
          </el-checkbox-group>
        </div>
      </div>

      <div class="setting-section">
        <div class="section-title">消息提醒方式</div>
        <div class="section-content">
          <el-checkbox-group v-model="notifyTypes">
            <el-checkbox label="弹窗提醒"></el-checkbox>
            <el-checkbox label="声音提醒"></el-checkbox>
            <el-checkbox label="浏览器标签闪烁"></el-checkbox>
          </el-checkbox-group>
        </div>
      </div>

      <div class="setting-section">
        <div class="section-title">组态页面排版</div>
        <div class="section-content">
          <el-radio-group v-model="layoutType">
            <el-radio label="原始比例"></el-radio>
            <el-radio label="宽度自适应"></el-radio>
            <el-radio label="完全自适应"></el-radio>
          </el-radio-group>
        </div>
      </div>

      <div class="setting-section">
        <div class="section-title">KG信息展示</div>
        <div class="section-content">
          <el-radio-group v-model="kgDisplay">
            <el-radio label="列表展示"></el-radio>
            <el-radio label="分组展示"></el-radio>
          </el-radio-group>
        </div>
      </div>

      <div class="form-actions">
        <el-button type="primary" @click="saveSettings" :loading="loading">保存</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { getUserSettings, updateUserSettings } from '@/api/user'

export default {
  name: 'SystemSettings',
  data() {
    return {
      messageTypes: [],
      notifyTypes: [],
      layoutType: '',
      kgDisplay: '',
      loading: false
    }
  },
  mounted() {
    this.loadSettings()
  },
  methods: {
    async loadSettings() {
      try {
        const res = await getUserSettings()
        this.messageTypes = res.data.message_types || []
        this.notifyTypes = res.data.notify_types || []
        this.layoutType = res.data.layout_type || '原始比例'
        this.kgDisplay = res.data.kg_display || '列表展示'
      } catch (error) {
        console.error('加载失败:', error)
      }
    },
    async saveSettings() {
      this.loading = true
      try {
        await updateUserSettings({
          message_types: this.messageTypes,
          notify_types: this.notifyTypes,
          layout_type: this.layoutType,
          kg_display: this.kgDisplay
        })
        this.$message.success('设置已保存')
      } catch (error) {
        console.error('保存失败:', error)
      } finally {
        this.loading = false
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

.setting-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
}

.section-content {
  padding-left: 10px;
}

.form-actions {
  margin-top: 40px;
}
</style>
