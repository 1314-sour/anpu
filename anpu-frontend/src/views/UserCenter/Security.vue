<template>
  <div class="page-content">
    <div class="page-header">安全设置</div>
    <div class="page-body">
      <!-- 用户头像信息 -->
      <div class="user-info-section">
        <div class="avatar-box">
          <img :src="userInfo.avatar || defaultAvatar" alt="avatar" class="user-avatar">
          <div class="modify-avatar" @click="dialogVisible = true">修改头像</div>
        </div>
        <div class="info-box">
          <div class="info-row">登录账号：<span>{{ userInfo.username }}</span></div>
          <div class="info-row">注册时间：<span>{{ userInfo.registerTime }}</span></div>
        </div>
      </div>

      <!-- 安全强度 -->
      <div class="security-level-section">
        <span>您当前的账号安全程度</span>
        <el-progress :percentage="securityScore" :format="format" :color="scoreColor" class="security-progress"></el-progress>
        <span class="level-text">安全等级：<span :style="{color: scoreColor}">{{ securityLevel }}</span></span>
        <span class="level-desc">{{ scoreDesc }}</span>
      </div>

      <!-- 设置列表 -->
      <div class="settings-list">
        <div class="setting-item">
          <div class="item-icon"><i class="el-icon-lock"></i></div>
          <div class="item-content">
            <div class="item-title">登录密码</div>
            <div class="item-desc">安全性高的密码可以使账号更安全。建议您定期更换密码，设置一个包含字母，符号或数字中至少两项且长度超过6位的密码。</div>
          </div>
          <div class="item-action">
            <span class="status-text success"><i class="el-icon-circle-check"></i> 已设置</span>
            <span class="separator">|</span>
            <el-button type="text" @click="showPasswordDialog">修改</el-button>
          </div>
        </div>

        <div class="setting-item">
          <div class="item-icon"><i class="el-icon-mobile-phone"></i></div>
          <div class="item-content">
            <div class="item-title">手机绑定</div>
            <div class="item-desc">您已绑定了手机 {{ userInfo.phone || '未绑定' }} [您的手机为安全手机，若已丢失或停用，请立即更换，避免账户被盗]</div>
          </div>
          <div class="item-action">
            <span v-if="userInfo.phone" class="status-text success"><i class="el-icon-circle-check"></i> 已设置</span>
            <span v-else class="status-text warning"><i class="el-icon-warning-outline"></i> 未设置</span>
            <span class="separator">|</span>
            <el-button type="text" @click="showPhoneDialog">{{ userInfo.phone ? '修改' : '设置' }}</el-button>
          </div>
        </div>
        
        <div class="setting-item">
          <div class="item-icon"><i class="el-icon-message"></i></div>
          <div class="item-content">
            <div class="item-title">邮箱绑定</div>
            <div class="item-desc">您已绑定了邮箱 {{ userInfo.email || '未绑定' }} [您的邮箱为安全邮箱，若已丢失或停用，请立即更换，避免账户被盗]</div>
          </div>
          <div class="item-action">
            <span v-if="userInfo.email" class="status-text success"><i class="el-icon-circle-check"></i> 已设置</span>
            <span v-else class="status-text warning"><i class="el-icon-warning-outline"></i> 未设置</span>
            <span class="separator">|</span>
            <el-button type="text" @click="showEmailDialog">{{ userInfo.email ? '修改' : '设置' }}</el-button>
          </div>
        </div>

        <div class="setting-item">
          <div class="item-icon"><i class="el-icon-question"></i></div>
          <div class="item-content">
            <div class="item-title">密保问题</div>
            <div class="item-desc">建议您设置三个密保问题，如果忘记密码或需要人员找回及查询，查找修改相应的资料更安全。</div>
          </div>
          <div class="item-action">
            <span v-if="userInfo.securityQuestionSet" class="status-text success"><i class="el-icon-circle-check"></i> 已设置</span>
            <span v-else class="status-text warning"><i class="el-icon-warning-outline"></i> 未设置</span>
            <span class="separator">|</span>
            <el-button type="text" @click="showSecurityDialog">{{ userInfo.securityQuestionSet ? '修改' : '设置' }}</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改头像弹窗 -->
    <el-dialog
      title="修改头像"
      :visible.sync="dialogVisible"
      width="500px">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="本地上传" name="local">
          <div class="upload-container">
            <el-upload
              class="avatar-uploader"
              action="https://jsonplaceholder.typicode.com/posts/"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload">
              <img v-if="imageUrl" :src="imageUrl" class="avatar">
              <i v-else class="el-icon-plus avatar-uploader-icon"></i>
            </el-upload>
            <div class="upload-tip">
              <p>建议上传尺寸：150x150</p>
              <p>支持JPG, PNG, GIF, BMP, JPEG格式图片，文件大小小于300K</p>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="系统头像" name="system">
          <p style="text-align:center;color:#999;">暂无系统头像</p>
        </el-tab-pane>
      </el-tabs>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogVisible = false">确 认</el-button>
        <el-button @click="dialogVisible = false">取 消</el-button>
      </span>
    </el-dialog>

    <!-- 修改密码弹窗 -->
    <el-dialog
      title="修改登录密码"
      :visible.sync="passwordDialogVisible"
      width="600px"
      :close-on-click-modal="false">
      <el-steps :active="passwordStep" align-center finish-status="success">
        <el-step title="验证身份"></el-step>
        <el-step title="修改登录密码"></el-step>
        <el-step title="完成"></el-step>
      </el-steps>
      
      <div style="margin-top: 30px;">
        <!-- 步骤1: 验证身份 -->
        <div v-if="passwordStep === 0">
          <el-form :model="passwordForm" label-width="120px" style="max-width: 400px; margin: 0 auto;">
            <el-form-item label="账户：">
              <span>{{ userInfo.username }}</span>
            </el-form-item>
            <el-form-item label="原密码：" required>
              <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码"></el-input>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 步骤2: 修改密码 -->
        <div v-if="passwordStep === 1">
          <el-form :model="passwordForm" label-width="120px" style="max-width: 400px; margin: 0 auto;">
            <el-form-item label="新密码：" required>
              <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码"></el-input>
            </el-form-item>
            <el-form-item label="确认密码：" required>
              <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码"></el-input>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 步骤3: 完成 -->
        <div v-if="passwordStep === 2" style="text-align: center; padding: 40px 0;">
          <i class="el-icon-success" style="font-size: 60px; color: #67c23a;"></i>
          <p style="font-size: 16px; margin-top: 20px;">密码修改成功!</p>
        </div>
      </div>
      
      <span slot="footer" class="dialog-footer">
        <el-button v-if="passwordStep < 2" @click="passwordDialogVisible = false">取 消</el-button>
        <el-button v-if="passwordStep > 0 && passwordStep < 2" @click="passwordStep--">上一步</el-button>
        <el-button v-if="passwordStep < 2" type="primary" @click="handlePasswordNext" :loading="passwordLoading">{{ passwordStep === 1 ? '提交' : '下一步' }}</el-button>
        <el-button v-if="passwordStep === 2" type="primary" @click="passwordDialogVisible = false">完 成</el-button>
      </span>
    </el-dialog>

    <!-- 修改手机弹窗 -->
    <el-dialog
      title="修改手机绑定"
      :visible.sync="phoneDialogVisible"
      width="600px"
      :close-on-click-modal="false">
      <el-steps :active="phoneStep" align-center finish-status="success">
        <el-step title="验证身份"></el-step>
        <el-step title="绑定新手机"></el-step>
        <el-step title="完成"></el-step>
      </el-steps>
      
      <div style="margin-top: 30px;">
        <!-- 步骤1: 验证身份 -->
        <div v-if="phoneStep === 0">
          <el-form label-width="120px" style="max-width: 400px; margin: 0 auto;">
            <el-form-item label="账户：">
              <span>{{ userInfo.username }}</span>
            </el-form-item>
            <el-form-item label="当前手机：">
              <span>{{ userInfo.phone || '未绑定' }}</span>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 步骤2: 绑定新手机 -->
        <div v-if="phoneStep === 1">
          <el-form :model="phoneForm" label-width="120px" style="max-width: 400px; margin: 0 auto;">
            <el-form-item label="新手机号：" required>
              <el-input v-model="phoneForm.phone" placeholder="请输入新手机号"></el-input>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 步骤3: 完成 -->
        <div v-if="phoneStep === 2" style="text-align: center; padding: 40px 0;">
          <i class="el-icon-success" style="font-size: 60px; color: #67c23a;"></i>
          <p style="font-size: 16px; margin-top: 20px;">手机绑定成功!</p>
        </div>
      </div>
      
      <span slot="footer" class="dialog-footer">
        <el-button v-if="phoneStep < 2" @click="phoneDialogVisible = false">取 消</el-button>
        <el-button v-if="phoneStep > 0 && phoneStep < 2" @click="phoneStep--">上一步</el-button>
        <el-button v-if="phoneStep < 2" type="primary" @click="handlePhoneNext" :loading="phoneLoading">{{ phoneStep === 1 ? '提交' : '下一步' }}</el-button>
        <el-button v-if="phoneStep === 2" type="primary" @click="phoneDialogVisible = false">完 成</el-button>
      </span>
    </el-dialog>

    <!-- 修改邮箱弹窗 -->
    <el-dialog
      title="修改邮箱绑定"
      :visible.sync="emailDialogVisible"
      width="600px"
      :close-on-click-modal="false">
      <el-steps :active="emailStep" align-center finish-status="success">
        <el-step title="验证身份"></el-step>
        <el-step title="绑定新邮箱"></el-step>
        <el-step title="完成"></el-step>
      </el-steps>
      
      <div style="margin-top: 30px;">
        <!-- 步骤1: 验证身份 -->
        <div v-if="emailStep === 0">
          <el-form label-width="120px" style="max-width: 400px; margin: 0 auto;">
            <el-form-item label="账户：">
              <span>{{ userInfo.username }}</span>
            </el-form-item>
            <el-form-item label="当前邮箱：">
              <span>{{ userInfo.email || '未绑定' }}</span>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 步骤2: 绑定新邮箱 -->
        <div v-if="emailStep === 1">
          <el-form :model="emailForm" label-width="120px" style="max-width: 400px; margin: 0 auto;">
            <el-form-item label="新邮箱：" required>
              <el-input v-model="emailForm.email" placeholder="请输入新邮箱地址"></el-input>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 步骤3: 完成 -->
        <div v-if="emailStep === 2" style="text-align: center; padding: 40px 0;">
          <i class="el-icon-success" style="font-size: 60px; color: #67c23a;"></i>
          <p style="font-size: 16px; margin-top: 20px;">邮箱绑定成功!</p>
        </div>
      </div>
      
      <span slot="footer" class="dialog-footer">
        <el-button v-if="emailStep < 2" @click="emailDialogVisible = false">取 消</el-button>
        <el-button v-if="emailStep > 0 && emailStep < 2" @click="emailStep--">上一步</el-button>
        <el-button v-if="emailStep < 2" type="primary" @click="handleEmailNext" :loading="emailLoading">{{ emailStep === 1 ? '提交' : '下一步' }}</el-button>
        <el-button v-if="emailStep === 2" type="primary" @click="emailDialogVisible = false">完 成</el-button>
      </span>
    </el-dialog>

    <!-- 设置密保问题弹窗 -->
    <el-dialog
      title="设置密保问题"
      :visible.sync="securityDialogVisible"
      width="600px"
      :close-on-click-modal="false">
      <el-form :model="securityForm" label-width="80px">
        <p style="color: #909399; margin-bottom: 20px;">为了您的账户安全,请设置密保问题</p>
        <el-form-item label="问题：" required>
          <el-input v-model="securityForm.question" placeholder="请输入密保问题"></el-input>
        </el-form-item>
        <el-form-item label="答案：" required>
          <el-input v-model="securityForm.answer" placeholder="请输入密保答案"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="securityDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleSecuritySubmit" :loading="securityLoading">提 交</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getUserProfile, changePassword, updateUserProfile } from '@/api/user'

export default {
  name: 'SecuritySettings',
  data() {
    return {
      dialogVisible: false,
      activeTab: 'local',
      imageUrl: '',
      defaultAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
      userInfo: {
        username: '',
        registerTime: '',
        avatar: '',
        phone: '',
        email: '',
        securityQuestionSet: false
      },
      // 修改密码
      passwordDialogVisible: false,
      passwordStep: 0,
      passwordLoading: false,
      passwordForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      // 修改手机
      phoneDialogVisible: false,
      phoneStep: 0,
      phoneLoading: false,
      phoneForm: {
        phone: ''
      },
      // 修改邮箱
      emailDialogVisible: false,
      emailStep: 0,
      emailLoading: false,
      emailForm: {
        email: ''
      },
      // 密保问题
      securityDialogVisible: false,
      securityLoading: false,
      securityForm: {
        question: '',
        answer: ''
      }
    };
  },
  mounted() {
    this.loadUserInfo()
  },
  computed: {
    securityScore() {
      let score = 25; // 基础分（密码已设置）
      if (this.userInfo.phone) score += 25;
      if (this.userInfo.email) score += 25;
      if (this.userInfo.securityQuestionSet) score += 25;
      return score;
    },
    securityLevel() {
      if (this.securityScore < 60) return '低';
      if (this.securityScore < 80) return '中';
      return '高';
    },
    scoreColor() {
      if (this.securityScore < 60) return '#f56c6c';
      if (this.securityScore < 80) return '#e6a23c';
      return '#67c23a';
    },
    scoreDesc() {
      if (this.securityScore < 60) return '存在风险，建议完善安全设置';
      if (this.securityScore < 80) return '安全等级一般，建议继续完善';
      return '账号非常安全';
    }
  },
  methods: {
    async loadUserInfo() {
      try {
        const res = await getUserProfile()
        this.userInfo = {
          username: res.data.username,
          registerTime: res.data.register_time || '',
          avatar: res.data.avatar || '',
          phone: res.data.phone || '',
          email: res.data.email || '',
          securityQuestionSet: res.data.security_question_set || false
        }
      } catch (error) {
        console.error('加载失败:', error)
      }
    },
    format(percentage) {
      return percentage === 100 ? '满' : `${percentage}`;
    },
    handleAvatarSuccess(res, file) {
      this.imageUrl = URL.createObjectURL(file.raw);
    },
    beforeAvatarUpload(file) {
      const isLt300K = file.size / 1024 < 300;
      if (!isLt300K) {
        this.$message.error('上传头像图片大小不能超过 300KB!');
      }
      return isLt300K;
    },
    
    // 修改密码相关
    showPasswordDialog() {
      this.passwordStep = 0
      this.passwordForm = { oldPassword: '', newPassword: '', confirmPassword: '' }
      this.passwordDialogVisible = true
    },
    async handlePasswordNext() {
      if (this.passwordStep === 0) {
        // 验证原密码
        if (!this.passwordForm.oldPassword) {
          this.$message.warning('请输入原密码')
          return
        }
        this.passwordStep = 1
      } else if (this.passwordStep === 1) {
        // 提交修改
        if (!this.passwordForm.newPassword) {
          this.$message.warning('请输入新密码')
          return
        }
        if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
          this.$message.warning('两次密码输入不一致')
          return
        }
        if (this.passwordForm.newPassword.length < 6) {
          this.$message.warning('密码长度不能少于6位')
          return
        }
        
        this.passwordLoading = true
        try {
          await changePassword({
            old_password: this.passwordForm.oldPassword,
            new_password: this.passwordForm.newPassword
          })
          this.passwordStep = 2
        } catch (error) {
          console.error('修改失败:', error)
        } finally {
          this.passwordLoading = false
        }
      }
    },
    
    // 修改手机相关
    showPhoneDialog() {
      this.phoneStep = 0
      this.phoneForm = { phone: '' }
      this.phoneDialogVisible = true
    },
    async handlePhoneNext() {
      if (this.phoneStep === 0) {
        this.phoneStep = 1
      } else if (this.phoneStep === 1) {
        if (!this.phoneForm.phone) {
          this.$message.warning('请输入手机号')
          return
        }
        if (!/^1[3-9]\d{9}$/.test(this.phoneForm.phone)) {
          this.$message.warning('请输入正确的手机号')
          return
        }
        
        this.phoneLoading = true
        try {
          await updateUserProfile({ phone: this.phoneForm.phone })
          this.userInfo.phone = this.phoneForm.phone
          this.phoneStep = 2
        } catch (error) {
          console.error('修改失败:', error)
        } finally {
          this.phoneLoading = false
        }
      }
    },
    
    // 修改邮箱相关
    showEmailDialog() {
      this.emailStep = 0
      this.emailForm = { email: '' }
      this.emailDialogVisible = true
    },
    async handleEmailNext() {
      if (this.emailStep === 0) {
        this.emailStep = 1
      } else if (this.emailStep === 1) {
        if (!this.emailForm.email) {
          this.$message.warning('请输入邮箱地址')
          return
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.emailForm.email)) {
          this.$message.warning('请输入正确的邮箱地址')
          return
        }
        
        this.emailLoading = true
        try {
          await updateUserProfile({ email: this.emailForm.email })
          this.userInfo.email = this.emailForm.email
          this.emailStep = 2
        } catch (error) {
          console.error('修改失败:', error)
        } finally {
          this.emailLoading = false
        }
      }
    },
    
    // 设置密保问题相关
    showSecurityDialog() {
      this.securityForm = { question: '', answer: '' }
      this.securityDialogVisible = true
    },
    async handleSecuritySubmit() {
      if (!this.securityForm.question) {
        this.$message.warning('请输入密保问题')
        return
      }
      if (!this.securityForm.answer) {
        this.$message.warning('请输入密保答案')
        return
      }
      
      this.securityLoading = true
      try {
        await updateUserProfile({ security_question_set: true })
        this.userInfo.securityQuestionSet = true
        this.$message.success('密保问题设置成功')
        this.securityDialogVisible = false
      } catch (error) {
        console.error('设置失败:', error)
      } finally {
        this.securityLoading = false
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

.user-info-section {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.avatar-box {
  position: relative;
  cursor: pointer;
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  margin-right: 20px;
}

.modify-avatar {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 80px;
  height: 24px;
  line-height: 24px;
  background: rgba(0,0,0,0.6);
  color: #fff;
  text-align: center;
  font-size: 12px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  display: none;
}

.avatar-box:hover .modify-avatar {
  display: block;
}

.upload-container {
  display: flex;
  align-items: center;
  padding: 20px;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100px;
  height: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-uploader:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.avatar {
  width: 100px;
  height: 100px;
  display: block;
}

.upload-tip {
  margin-left: 20px;
  font-size: 12px;
  color: #999;
}

.upload-tip p {
  margin: 5px 0;
}

.upload-tip p:last-child {
  color: #e6a23c;
}

.info-row {
  margin-bottom: 10px;
  color: #606266;
  font-size: 14px;
}

.info-row span {
  font-weight: bold;
  color: #333;
}

.security-level-section {
  display: flex;
  align-items: center;
  padding: 20px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;
  font-size: 14px;
  color: #606266;
}

.security-progress {
  width: 200px;
  margin: 0 20px;
}

.level-low {
  color: #f56c6c;
  font-weight: bold;
}

.settings-list {
  margin-top: 20px;
}

.setting-item {
  display: flex;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #ebeef5;
}

.item-icon {
  font-size: 24px;
  color: #409EFF;
  margin-right: 20px;
  width: 40px;
  text-align: center;
}

.item-content {
  flex: 1;
}

.item-title {
  font-size: 16px;
  color: #333;
  margin-bottom: 5px;
}

.item-desc {
  font-size: 14px;
  color: #909399;
}

.item-action {
  width: 150px;
  text-align: right;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.status-text {
  font-size: 14px;
  margin-right: 10px;
}

.status-text.success {
  color: #67c23a;
}

.status-text.warning {
  color: #e6a23c;
}

.separator {
  color: #dcdfe6;
  margin: 0 10px;
}
</style>
