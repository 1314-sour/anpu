<template>
  <div class="page-content">
    <div class="page-header">意见反馈</div>
    <div class="page-body">
      <el-form :model="form" label-width="100px" class="feedback-form">
        <el-form-item label="反馈类型：">
          <el-select v-model="form.type" placeholder="请选择反馈类型" style="width: 100%;">
            <el-option label="功能问题" value="function"></el-option>
            <el-option label="优化建议" value="suggestion"></el-option>
            <el-option label="其他" value="other"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="建议内容：" required>
          <el-input
            type="textarea"
            :rows="8"
            placeholder="请输入您的意见，我们将不断优化体验"
            v-model="form.content">
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="onSubmit" :loading="loading">提交反馈</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import { submitFeedback } from '@/api/user'

export default {
  name: 'UserFeedback',
  data() {
    return {
      form: {
        type: 'function',
        content: ''
      },
      loading: false
    }
  },
  methods: {
    async onSubmit() {
      if (!this.form.content) {
        this.$message.warning('请输入建议内容')
        return
      }
      
      this.loading = true
      try {
        await submitFeedback({
          type: this.form.type,
          content: this.form.content
        })
        this.$message.success('反馈提交成功')
        this.form.content = ''
      } catch (error) {
        console.error('提交失败:', error)
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

.feedback-form {
  max-width: 600px;
}
</style>
