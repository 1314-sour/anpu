<template>
  <div class="user-center-container">
    <el-container class="content-box">
      <!-- 左侧侧边栏 -->
      <el-aside width="200px" class="sidebar">
        <div class="sidebar-header">账号管理</div>
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu"
          router
          text-color="#606266"
          active-text-color="#409EFF">
          <el-menu-item index="/user/security">
            <span>安全设置</span>
          </el-menu-item>
          <el-menu-item index="/user/profile">
            <span>基本资料</span>
          </el-menu-item>
          <el-menu-item index="/user/system">
            <span>系统设置</span>
          </el-menu-item>
          <el-menu-item index="/user/logs">
            <span>操作日志</span>
          </el-menu-item>
          <el-menu-item index="/user/feedback">
            <span>意见反馈</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'UserCenterLayout'
}
</script>

<style scoped>
.user-center-container {
  height: calc(100vh - 60px); /* 减去顶部导航栏高度 */
  background-color: #f0f2f5;
  padding: 20px;
  box-sizing: border-box;
}

.content-box {
  background-color: #fff;
  height: 100%;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.sidebar {
  border-right: 1px solid #e6e6e6;
  background-color: #fff;
}

.sidebar-header {
  height: 60px;
  line-height: 60px;
  padding-left: 20px;
  font-size: 16px;
  font-weight: bold;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}

.sidebar-menu {
  border-right: none;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
}

.el-menu-item.is-active {
  background-color: #e6f7ff;
  border-right: 3px solid #1890ff;
}

.main-content {
  padding: 0;
  overflow-y: auto;
}
</style>
