<template>
  <div class="home-container">
    <el-empty description="还没有任何项目">
      <el-button type="primary" size="small">创建项目</el-button>
    </el-empty>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home-container {
  padding: 20px;
  height: calc(100vh - 60px);
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
