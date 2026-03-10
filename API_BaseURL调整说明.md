# 前端 API BaseURL 调整说明

为配合 Nginx 在同域下将 `/api` 前缀代理到 FastAPI 服务，前端已改为使用相对路径 `/api` 作为统一的接口基地址。以下列出本次修改的具体文件、代码片段及目的，方便追踪与部署。

## 1. `anpu-frontend/src/api/request.js`

- 第 4 行将 `API_BASE_URL` 默认值由 `http://localhost:8000` 改为 `/api`，仍可通过 `VUE_APP_API_BASE_URL` 覆盖。
- 注释同步更新，强调默认走 `/api` 交由 Nginx 反向代理。

```js
// 统一的后端 API 地址，默认走 /api 交由 Nginx 反向代理
export const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api'

const service = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000
})
```

## 2. `anpu-frontend/src/views/Admin/DeviceDetail/BasicInfo.vue`

- `data()` 中的 `uploadUrl` 由 ``${API_BASE_URL}/api/v1/upload/image`` 改为 ``${API_BASE_URL}/v1/upload/image``，与上述策略保持一致。

```js
data() {
  return {
    uploadUrl: `${API_BASE_URL}/v1/upload/image`,
    // ...
  }
}
```

## 3. `anpu-frontend/vue.config.js`

- 在 `devServer` 中新增 `/api` 代理，将开发环境内 `/api/*` 请求转发至后端 `http://localhost:8000`（可通过 `VUE_APP_DEV_PROXY` 变量覆盖）；这样在本地运行 `npm run serve` 时同样可使用相对基址，避免 404 与跨域。

```js
module.exports = defineConfig({
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
```

---

完成以上调整后，前端发起的所有请求都会命中浏览器相对路径 `/api/...`，再由 Nginx 或开发代理转发到 FastAPI，彻底规避跨域问题。部署时只需在 Nginx 中配置 `location /api { proxy_pass http://后端服务; }` 即可。***
