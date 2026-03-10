const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 7000,
    proxy: {
      '/api': {
        target: process.env.VUE_APP_DEV_PROXY || 'http://localhost:8000',
        changeOrigin: true,
        ws: false
      }
    }
  }
})
