# Network Error 问题排查与解决

## 🔍 问题现象

前端页面显示 **Network Error** 错误

---

## ✅ 解决步骤

### 步骤1: 确认后端服务是否启动

**检查方法:**
```bash
# 检查8000端口是否被监听
netstat -ano | findstr :8000
```

**如果没有输出,说明后端未启动,需要启动后端:**
```bash
cd e:\AnPu\anpu-backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**成功标志:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

### 步骤2: 确认是否已登录

**Network Error 最常见原因: 用户未登录或token过期**

**解决方法:**
1. 访问登录页面: http://localhost:7002/login
2. 使用测试账号登录:
   - 账号: `admin`
   - 密码: `123456`
3. 登录成功后再访问用户中心页面

**验证登录状态:**
- 打开浏览器开发者工具 (F12)
- 进入 Application → Local Storage → http://localhost:7002
- 检查是否有 `token` 字段

---

### 步骤3: 检查前端控制台错误信息

**打开浏览器控制台 (F12):**
1. 切换到 Console 标签
2. 切换到 Network 标签
3. 刷新页面查看失败的请求

**常见错误及解决:**

#### 错误1: `ERR_CONNECTION_REFUSED`
**原因**: 后端服务未启动  
**解决**: 启动后端服务 (见步骤1)

#### 错误2: `401 Unauthorized`
**原因**: 未登录或token过期  
**解决**: 重新登录 (见步骤2)

#### 错误3: `CORS policy blocked`
**原因**: 跨域配置问题  
**解决**: 检查后端 `.env` 文件的 `CORS_ORIGINS` 配置

#### 错误4: `Request failed with status code 404`（登录接口）
**原因**: 将前端 `API_BASE_URL` 改为 `/api` 后, Vue 本地开发服务器(端口7000/7002) 会把请求落在自身, 由于 `vue.config.js` 未配置 `/api` 代理, `/api/v1/auth/login` 实际访问的是前端服务器而不是 FastAPI, 导致 404。  
**解决**: 在 `vue.config.js` 中为 `/api` 添加反向代理至 `http://localhost:8000`（后端服务）。已在当前仓库中补充如下配置:
```js
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
```
前端重启 `npm run serve` 后, 所有 `/api/*` 请求会自动转发到本地 FastAPI, 同域访问解决跨域问题。

---

### 步骤4: 测试API连通性

**使用测试脚本:**
```bash
cd e:\AnPu\anpu-backend
python test_api.py
```

**期望输出:**
```
=== 测试登录API ===
状态码: 200
响应: {'code': 200, 'message': '登录成功', ...}

=== 测试获取用户资料API ===
状态码: 200
响应: {'code': 200, 'message': '操作成功', ...}
```

如果显示 `连接失败`,说明后端服务未正常运行。

---

### 步骤5: 检查CORS配置

**检查后端 `.env` 文件:**
```bash
CORS_ORIGINS=http://localhost:8080,http://localhost:8081,http://localhost:7001,http://localhost:7002
```

**确保包含前端运行的端口 (如7002)**

修改后需要重启后端服务。

---

## 🛠️ 完整启动流程

### 1. 启动后端
```bash
cd e:\AnPu\anpu-backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端
```bash
cd e:\AnPu\anpu-frontend
npm run serve
```

### 3. 访问登录页面
```
http://localhost:7002/login
```

### 4. 登录系统
- 账号: `admin`
- 密码: `123456`

### 5. 访问用户中心
登录成功后,点击左侧菜单 "账号管理" 进入用户中心各功能页面。

---

## 📝 错误信息升级

我已经优化了错误提示,现在会显示更详细的信息:

- ✅ `网络连接失败,请检查后端服务是否启动(http://localhost:8000)`
- ✅ `登录已过期,请重新登录` (会自动跳转到登录页)
- ✅ `请求超时,请检查网络`
- ✅ `没有权限访问`
- ✅ `服务器错误`

---

## 🎯 快速诊断

**如果看到 "Network Error",按顺序检查:**

1. ✅ 后端是否在运行? (netstat -ano | findstr :8000)
2. ✅ 是否已登录? (F12 → Application → Local Storage → token)
3. ✅ 浏览器控制台有什么错误? (F12 → Console)
4. ✅ CORS配置是否正确? (.env 文件)

---

## 💡 常见场景

### 场景1: 刚打开页面就显示 Network Error
**原因**: 页面mounted时自动请求API,但用户未登录  
**解决**: 先访问 /login 登录

### 场景2: 登录后立即显示 Network Error
**原因**: 后端服务未启动  
**解决**: 启动后端服务

### 场景3: 之前正常,突然显示 Network Error
**原因**: token过期 (默认30分钟)  
**解决**: 重新登录

---

## 🔧 紧急修复

如果上述方法都无效,执行完整重启:

```bash
# 1. 关闭所有服务 (Ctrl+C)

# 2. 清理前端缓存
cd e:\AnPu\anpu-frontend
npm cache clean --force

# 3. 重启后端
cd e:\AnPu\anpu-backend
python -m uvicorn app.main:app --reload

# 4. 重启前端
cd e:\AnPu\anpu-frontend
npm run serve

# 5. 清除浏览器缓存
# Ctrl+Shift+Delete → 清除缓存和Cookie

# 6. 重新登录
# http://localhost:7002/login
```

---

现在刷新页面,错误提示会更加友好和详细! 🎉
