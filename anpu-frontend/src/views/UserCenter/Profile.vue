<template>
  <div class="page-content">
    <div class="page-header">基本资料</div>
    <div class="page-body">
      <el-alert
        title="温馨提示：请完善以下信息方便我们更好的为您服务"
        type="warning"
        show-icon
        :closable="false"
        class="tip-alert">
      </el-alert>

      <el-form :model="form" label-width="100px" class="profile-form">
        <el-form-item label="用户名：">
          <span>{{ form.username }}</span>
        </el-form-item>
        
        <el-form-item label="联系电话：">
          <span>{{ form.phone }}</span>
        </el-form-item>
        
        <el-form-item label="邮箱：">
          <span>{{ form.email }}</span>
        </el-form-item>
        
        <el-form-item label="联系人：" required>
          <el-input v-model="form.contactPerson" placeholder="请输入联系人姓名"></el-input>
        </el-form-item>
        
        <el-form-item label="详细地址：">
          <el-input v-model="form.address" placeholder="请输入详细地址"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="onSubmit" :loading="loading">保存</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import { getUserProfile, updateUserProfile } from '@/api/user'

export default {
  name: 'UserProfile',
  data() {
    return {
      form: {
        username: '',
        phone: '',
        email: '',
        contactPerson: '',
        address: ''
      },
      loading: false
    }
  },
  mounted() {
    this.loadProfile()
  },
  methods: {
    async loadProfile() {
      try {
        const res = await getUserProfile()
        this.form = {
          username: res.data.username,
          phone: res.data.phone || '',
          email: res.data.email || '',
          contactPerson: res.data.contact_person || '',
          address: res.data.address || ''
        }
      } catch (error) {
        console.error('加载失败:', error)
      }
    },
    async onSubmit() {
      this.loading = true
      try {
        await updateUserProfile({
          contact_person: this.form.contactPerson,
          address: this.form.address
        })
        this.$message.success('保存成功')
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

.tip-alert {
  margin-bottom: 30px;
}

.profile-form {
  max-width: 500px;
}
</style>
