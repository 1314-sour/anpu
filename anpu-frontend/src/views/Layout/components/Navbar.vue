<template>
  <div class="navbar">
    <div class="left-section">
      <img src="@/assets/anpu-logo.png" alt="Logo" class="nav-logo" />
      <span class="nav-title">安普物联网云平台</span>
    </div>
    <div class="right-section">
      <!-- 菜单区域 -->
      <div class="nav-menu-container">
        <!-- 设备监控 下拉菜单 -->
        <el-dropdown class="nav-dropdown" @command="handleCommand">
          <span class="el-dropdown-link">
            <i class="el-icon-monitor"></i> 设备监控 <i class="el-icon-arrow-down el-icon--right"></i>
          </span>
          <el-dropdown-menu slot="dropdown" class="custom-dropdown-menu">
            <el-dropdown-item command="deviceMonitor">
              <i class="el-icon-monitor"></i> 设备监控
            </el-dropdown-item>
            <el-dropdown-item command="gmList">
              <i class="el-icon-s-operation"></i> GM列表
            </el-dropdown-item>
            <el-dropdown-item command="gmGroup">
              <i class="el-icon-connection"></i> GM分组
            </el-dropdown-item>
            <el-dropdown-item command="operationCenter">
              <i class="el-icon-data-line"></i> 运营中心
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>

              <!-- 数据汇总 下拉菜单 -->
        <el-dropdown class="nav-dropdown" @command="handleCommand">
          <span class="el-dropdown-link">
            <i class="el-icon-s-data"></i> 数据汇总 <i class="el-icon-arrow-down el-icon--right"></i>
          </span>
          <el-dropdown-menu slot="dropdown" class="custom-dropdown-menu">
            <el-dropdown-item command="dataCenter">
              <i class="el-icon-s-data"></i> 数据中心
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>

        <!-- 设备地图 (无下拉) -->
        <div class="nav-item hover-effect">
          <i class="el-icon-location-outline"></i> 设备地图
        </div>

        <!-- 后台管理 (超级管理员、安普员工、企业管理员可见) -->
        <div class="nav-item hover-effect" v-if="isAdmin" @click="goToAdmin">
          <i class="el-icon-setting"></i> 后台管理
        </div>
      </div>
      
      <div class="nav-actions">
        <!-- 消息通知 -->
        <div class="action-item hover-effect" @click="goToMessages">
          <el-badge :value="unreadCount > 0 ? unreadCount : null" class="item">
            <i class="el-icon-message-solid"></i> 消息
          </el-badge>
        </div>

        <!-- 用户中心 下拉菜单 -->
        <el-dropdown class="user-dropdown" trigger="hover" @command="handleUserCommand">
          <span class="el-dropdown-link">
            <i class="el-icon-user"></i> {{ username }} <i class="el-icon-arrow-down el-icon--right"></i>
          </span>
          <el-dropdown-menu slot="dropdown" class="user-dropdown-menu">
            <el-dropdown-item command="security">
              <i class="el-icon-circle-check"></i> 安全设置
            </el-dropdown-item>
            <el-dropdown-item command="profile">
              <i class="el-icon-document"></i> 基本资料
            </el-dropdown-item>
            <el-dropdown-item command="system">
              <i class="el-icon-setting"></i> 系统设置
            </el-dropdown-item>
            <el-dropdown-item command="logs">
              <i class="el-icon-date"></i> 操作日志
            </el-dropdown-item>
            <el-dropdown-item command="feedback">
              <i class="el-icon-chat-dot-square"></i> 意见反馈
            </el-dropdown-item>
            <el-dropdown-item command="logout">
              <i class="el-icon-switch-button"></i> 退出
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

// 角色常量定义
const UserRole = {
  SUPER_ADMIN: 'super_admin',          // 超级管理员
  ANPU_STAFF: 'anpu_staff',            // 安普员工
  ENTERPRISE_ADMIN: 'enterprise_admin', // 企业管理员
  ENTERPRISE_STAFF: 'enterprise_staff'  // 企业员工
}

// 具有管理权限的角色
const ADMIN_ROLES = [UserRole.SUPER_ADMIN, UserRole.ANPU_STAFF, UserRole.ENTERPRISE_ADMIN]
// 安普内部角色
const ANPU_ROLES = [UserRole.SUPER_ADMIN, UserRole.ANPU_STAFF]

export default {
  name: 'TopNavbar',
  data() {
    return {
      username: localStorage.getItem('username') || '用户',
      role: localStorage.getItem('role') || 'enterprise_staff'
    }
  },
  computed: {
    ...mapGetters(['unreadCount']),
    // 是否是管理员角色（有后台管理权限）
    isAdmin() {
      return ADMIN_ROLES.includes(this.role)
    },
    // 是否是安普内部角色
    isAnpuStaff() {
      return ANPU_ROLES.includes(this.role)
    },
    // 是否是超级管理员
    isSuperAdmin() {
      return this.role === UserRole.SUPER_ADMIN
    }
  },
  mounted() {
    this.$store.dispatch('fetchUnreadCount')
    // 每30秒刷新一次未读消息数量
    this.timer = setInterval(() => {
      this.$store.dispatch('fetchUnreadCount')
    }, 30000)
  },
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  methods: {
    goToAdmin() {
      if (this.$route.path !== '/admin/device-list') {
        this.$router.push('/admin/device-list');
      }
    },
    goToMessages() {
      if (this.$route.path !== '/message/all') {
        this.$router.push('/message/all');
      }
    },

    handleCommand(command) {
      this.$message(`点击了菜单: ${command}`);
      // 实际开发中这里会跳转路由，例如:
      // this.$router.push({ name: command });
    },
    handleUserCommand(command) {
      if (command === 'logout') {
        this.logout();
      } else {
        const routeMap = {
          security: '/user/security',
          profile: '/user/profile',
          system: '/user/system',
          logs: '/user/logs',
          feedback: '/user/feedback'
        };
        if (routeMap[command]) {
          // 避免重复导航
          if (this.$route.path !== routeMap[command]) {
            this.$router.push(routeMap[command]);
          }
        } else {
          this.$message(`点击了用户菜单: ${command}`);
        }
      }
    },
    logout() {
      this.$confirm('确认退出登录吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$router.push('/login');
        this.$message({
          type: 'success',
          message: '退出成功!'
        });
      }).catch(() => {});
    }
  }
}
</script>

<style scoped>
.navbar {
  height: 60px;
  background: linear-gradient(90deg, #1e5799 0%, #2989d8 50%, #207cca 100%); /* 蓝色渐变背景 */
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  color: white;
  z-index: 1000; /* 确保在最上层 */
}

.left-section {
  display: flex;
  align-items: center;
  min-width: 200px;
}

.nav-logo {
  height: 30px;
  margin-right: 10px;
}

.nav-title {
  font-size: 18px;
  font-weight: bold;
  white-space: nowrap;
}

.right-section {
  display: flex;
  align-items: center;
  flex: 1;
  justify-content: flex-start; /* 让菜单紧跟 Logo 区域之后，或者改为 flex-end 靠右 */
  margin-left: 40px;
}

/* 菜单容器 */
.nav-menu-container {
  display: flex;
  align-items: center;
  margin-right: auto; /* 将右侧的用户信息推到最右边 */
}

.nav-dropdown {
  color: #fff;
  cursor: pointer;
  padding: 0 15px;
  height: 60px;
  line-height: 60px;
  display: flex;
  align-items: center;
  transition: background-color 0.3s;
}

.nav-dropdown:hover, .nav-item:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.nav-item {
  cursor: pointer;
  padding: 0 15px;
  height: 60px;
  line-height: 60px;
  display: flex;
  align-items: center;
  font-size: 14px;
}

.nav-item i {
  margin-right: 5px;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.el-dropdown-link i {
  margin-right: 5px;
}

.el-icon-arrow-down {
  margin-left: 5px;
  font-size: 12px;
}

/* 右侧操作区 */
.nav-actions {
  display: flex;
  align-items: center;
}

.action-item {
  margin-right: 20px;
  cursor: pointer;
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 10px;
}

.action-item:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.user-dropdown {
  color: #fff;
  cursor: pointer;
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 15px;
}

.user-dropdown:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

/* 调整 Badge 样式以匹配设计图 */
::v-deep .el-badge__content.is-fixed {
  top: 15px;
  right: 0px;
}

.el-icon-message-solid {
  margin-right: 5px;
}
</style>

<style>
/* 全局样式覆盖，用于下拉菜单 */
.custom-dropdown-menu {
  margin-top: 0 !important;
  border-radius: 4px;
  padding: 5px 0;
}

.custom-dropdown-menu .el-dropdown-menu__item {
  padding: 0 20px;
  line-height: 36px;
  font-size: 14px;
}

.custom-dropdown-menu .el-dropdown-menu__item i {
  margin-right: 8px;
}

.user-dropdown-menu {
  margin-top: 0 !important;
  min-width: 120px;
}

.user-dropdown-menu .el-dropdown-menu__item {
  font-size: 14px;
  padding: 0 20px;
  line-height: 36px;
}

.user-dropdown-menu .el-dropdown-menu__item i {
  margin-right: 8px;
}
</style>
