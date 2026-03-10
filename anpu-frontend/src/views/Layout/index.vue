<template>
  <div class="app-wrapper">
    <div class="fixed-header">
      <top-navbar />
    </div>
    <div class="main-container">
      <transition name="fade-transform" mode="out-in">
        <router-view />
      </transition>
    </div>
  </div>
</template>

<script>
import TopNavbar from './components/Navbar'

export default {
  name: 'MainLayout',
  components: {
    TopNavbar
  }
}
</script>

<style scoped>
.app-wrapper {
  position: relative;
  height: 100%;
  width: 100%;
}

.fixed-header {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 9;
  width: 100%;
  height: 60px; /* 与 Navbar 高度一致 */
}

.main-container {
  padding-top: 60px; /* 留出导航栏高度 */
  min-height: 100vh;
  background-color: #f0f2f5; /* 浅灰背景 */
  box-sizing: border-box;
}

/* 简单的页面切换动画 */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all .5s;
}

.fade-transform-enter {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
