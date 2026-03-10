<template>
  <div class="message-center-container">
    <el-container class="content-box">
      <!-- 左侧侧边栏 -->
      <el-aside width="200px" class="sidebar">
        <div class="sidebar-header">消息中心</div>
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu"
          router
          text-color="#606266"
          active-text-color="#409EFF">
          <el-menu-item index="/message/all">
            <span>全部消息</span>
          </el-menu-item>
          <el-menu-item index="/message/read">
            <span>已读消息</span>
          </el-menu-item>
          <el-menu-item index="/message/unread">
            <span style="display:flex;justify-content:space-between;align-items:center;width:100%">
              未读消息
              <el-badge :value="unreadCount > 0 ? unreadCount : null" class="mark" type="danger" />
            </span>
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
import { mapGetters } from 'vuex'

export default {
  name: 'MessageCenterLayout',
  computed: {
    ...mapGetters(['unreadCount'])
  },
  mounted() {
    this.$store.dispatch('fetchUnreadCount')
  }
}
</script>

<style scoped>
.message-center-container {
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

/* 调整未读消息徽标位置 */
::v-deep .el-badge__content.is-fixed {
  top: 0;
  right: 10px;
}
</style>
