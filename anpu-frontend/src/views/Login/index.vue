<template>
  <div class="login-container">
    <!-- 顶部 Logo 和 语言切换 -->
    <div class="login-header">
      <div class="logo-container">
        <img src="@/assets/anpu-logo.png" alt="Logo" class="logo" />
        <span class="platform-name">安普物联网云平台</span>
      </div>
      <div class="language-switch">
        <el-dropdown>
          <span class="el-dropdown-link">
            语言/language<i class="el-icon-arrow-down el-icon--right"></i>
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item>中文</el-dropdown-item>
            <el-dropdown-item>English</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-box">
      <div class="login-title">欢迎登录</div>
      <div class="login-subtitle">公共场所不建议记住账号，以防账号丢失</div>
      
      <el-form :model="loginForm" :rules="rules" ref="loginForm" class="login-form">
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="账号" 
            prefix-icon="el-icon-user">
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="密码" 
            prefix-icon="el-icon-lock"
            @keyup.enter.native="handleLogin">
          </el-input>
        </el-form-item>

        <div class="login-options">
          <el-checkbox v-model="loginForm.remember">记住账号</el-checkbox>
          <el-link type="info" :underline="false">忘记密码</el-link>
        </div>

        <el-form-item>
          <el-button 
            type="primary" 
            class="login-button" 
            :loading="loading"
            @click="handleLogin">
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import { login } from '@/api/auth'

export default {
  name: 'LoginView',
  data() {
    return {
      loginForm: {
        username: '',
        password: '',
        remember: false
      },
      rules: {
        username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
      },
      loading: false
    }
  },
  mounted() {
    // 如果记住账号,从localStorage读取
    const savedUsername = localStorage.getItem('savedUsername')
    if (savedUsername) {
      this.loginForm.username = savedUsername
      this.loginForm.remember = true
    }
  },
  methods: {
    handleLogin() {
      this.$refs.loginForm.validate(async (valid) => {
        if (!valid) return false
        
        this.loading = true
        
        try {
          // 调用登录API
          const response = await login({
            username: this.loginForm.username,
            password: this.loginForm.password
          })
          
          // 登录成功
          const { token, refresh_token, user_info } = response.data
          
          // 保存token和用户信息
          localStorage.setItem('token', token)
          localStorage.setItem('refreshToken', refresh_token)
          localStorage.setItem('userInfo', JSON.stringify(user_info))
          localStorage.setItem('username', user_info.username)
          localStorage.setItem('role', user_info.role)
          
          // 记住账号
          if (this.loginForm.remember) {
            localStorage.setItem('savedUsername', this.loginForm.username)
          } else {
            localStorage.removeItem('savedUsername')
          }
          
          this.$message.success('登录成功')
          
          // 跳转到首页
          this.$router.push('/home')
          
        } catch (error) {
          console.error('登录失败:', error)
          // 错误信息已在axios拦截器中显示
        } finally {
          this.loading = false
        }
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  background: url('~@/assets/login-background.jpg') no-repeat center center;
  background-size: cover;
  position: relative;
  overflow: hidden;
}

.login-header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  box-sizing: border-box;
  background-color: rgba(255, 255, 255, 0.9); /* 稍微带点背景色以便看清，原图是白色背景条 */
  background: #fff; 
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  height: 30px;
  margin-right: 10px;
}

.platform-name {
  font-size: 20px;
  font-weight: bold;
  color: #1a3b8e; /* 深蓝色 */
}

.language-switch {
  cursor: pointer;
  color: #666;
}

.login-box {
  position: absolute;
  top: 50%;
  right: 15%; /* 靠右显示 */
  transform: translateY(-50%);
  width: 360px;
  background: #fff;
  padding: 30px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-title {
  font-size: 22px;
  color: #333;
  margin-bottom: 10px;
}

.login-subtitle {
  font-size: 12px;
  color: #e6a23c; /* 警告黄 */
  background-color: #fdf6ec;
  padding: 8px;
  margin-bottom: 20px;
  border: 1px solid #faecd8;
}

.login-form {
  margin-top: 20px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  background-color: #405db4; /* 按钮蓝 */
  border-color: #405db4;
}
</style>
