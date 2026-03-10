<script setup>
import IoTDashboard from '@/components/IoTDashboard.vue';
</script>

<template>
  <div class="data-summary-page">
    <div class="dashboard-wrapper">
      <IoTDashboard />
    </div>
  </div>
</template>

<style scoped>
/* 1. 去除页面的 padding 和 背景色，让大屏撑满 */
.data-summary-page {
  padding: 0;
  margin: 0;
  width: 100%;
  height: 100%;
  background-color: transparent; /* 去除灰色背景 */
  overflow: hidden; /* 防止出现双重滚动条 */
}

/* 2. 关键：动态计算高度 */
.dashboard-wrapper {
  width: 100%;
  
  /* calc(100vh - 84px) 的含义：
     100vh = 屏幕总高度
     - 84px = 减去顶部导航栏(Navbar)和标签栏(TagsView)的大致高度
     
     *如果保存后发现底部还有留白，可以把 84px 改小（例如 50px）
     *如果发现出现了垂直滚动条，可以把 84px 改大（例如 100px）
  */
  height: calc(100vh - 84px);
  
  position: relative;
  background-color: #050e24; /* 兜底背景色 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
</style>