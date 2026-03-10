# 网络错误 & 登录报错——需修改的代码及位置（原因就是后端响应不到前端的请求）

为快速修复“前端 Network Error / 后端 `error reading bcrypt version`”问题，按照下表逐项修改对应文件与行号即可。

---
## 前置（在.env文件中修改以下配置）
 一、修改数据库相关配置

 二、修改CORS，添加端口响应域名


## 一、前端

| 文件 | 位置 | 需要修改的代码 |
| --- | --- | --- |
| `anpu-frontend/src/api/request.js` | `:1-104` | 新增 `API_BASE_URL` 常量并在 axios/错误提示中统一使用。 |
| `anpu-frontend/src/views/Admin/DeviceDetail/BasicInfo.vue` | `:179-205` | 引入 `API_BASE_URL` 并调整 `uploadUrl`。 |

**完整修改代码：**

```javascript
// anpu-frontend/src/api/request.js
import axios from 'axios'
import { Message } from 'element-ui'

// 统一的后端 API 地址，支持通过环境变量覆盖
export const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000'

// 创建axios实例
const service = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000  // 增加到30秒
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      Message({ message: res.message || '请求失败', type: 'error', duration: 3000 })
      if (res.code === 401 && !response.config.url.includes('/auth/login')) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        setTimeout(() => { window.location.href = '/login' }, 1500)
      }
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  error => {
    let message = '网络错误'
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        message = '登录已过期,请重新登录'
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        setTimeout(() => { window.location.href = '/login' }, 1500)
      } else if (status === 403) {
        message = '没有权限访问'
      } else if (status === 404) {
        message = '请求的资源不存在'
      } else if (status === 500) {
        message = '服务器错误'
      } else if (data && data.message) {
        message = data.message
      }
    } else if (error.request) {
      if (error.code === 'ECONNABORTED') {
        message = '请求超时,请检查网络'
      } else if (error.message.includes('Network Error')) {
        message = `网络连接失败,请检查后端服务是否启动(${API_BASE_URL})`
      } else {
        message = '网络错误,请稍后重试'
      }
    } else {
      message = error.message || '未知错误'
    }
    Message({ message, type: 'error', duration: 5000 })
    return Promise.reject(error)
  }
)

export default service
```

```javascript
// anpu-frontend/src/views/Admin/DeviceDetail/BasicInfo.vue（节选）
import { createDevice, updateDevice, getGroups, getDeviceDetail, checkDeviceName } from '@/api/device'
import { API_BASE_URL } from '@/api/request'

export default {
  ...
  data() {
    return {
      loading: false,
      showMoreFields: false,
      showNameError: false,
      groupList: [],
      uploadUrl: `${API_BASE_URL}/api/v1/upload/image`,
      uploadHeaders: {
        'Authorization': 'Bearer ' + localStorage.getItem('token')
      },
      form: { ... }
    }
  },
  ...
}
```

---

## 二、后端

| 文件 | 位置 | 需要修改的代码 |
| --- | --- | --- |
| `anpu-backend/app/utils/security.py` | `:1-41` | 用 `bcrypt` 替换 Passlib，实现密码哈希与校验。 |
| `anpu-backend/requirements.txt` | `:12-16` | 删除 `passlib[bcrypt]==1.7.4`，保留 `bcrypt==3.2.2`。 |
| `anpu-backend/.env` | `:12-16` | 将 `DATABASE_URL` 调整为实际数据库连接串；若无 MySQL 环境可直接删除该行以回退到 SQLite。 |

**完整修改代码：**

```python
# anpu-backend/app/utils/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from ..config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    if not password:
        raise ValueError("密码不能为空")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    ...
```

```text
# anpu-backend/requirements.txt（节选）
# 安全认证
python-jose[cryptography]==3.3.0
bcrypt==3.2.2
python-dotenv==1.0.0
```

---

## 三、文档同步（保持环境一致）

| 文件 | 位置 | 需要修改的内容 |
| --- | --- | --- |
| `Network_Error_解决方案.md` | “步骤6: 校验 bcrypt 依赖” | 更新为：卸载 Passlib → 重新安装 `requirements.txt`，说明新方案直接使用 `bcrypt`。 |
| `项目开发文档.md` | 技术栈表 (`:31`)、bcrypt 说明 (`:1224`) | 改写为 “Bcrypt (bcrypt 模块)” 并提供 `hashpw/checkpw` 示例。 |
| `docker构建说明文档.md` | 依赖表、requirements 片段、运行提示 | 去掉 Passlib 描述，强调安装 `bcrypt` 并清理旧依赖。 |

---

## 四、执行顺序

1. 修改上述文件后，在后端虚拟环境执行：
   ```bash
   pip uninstall -y passlib
   pip install --upgrade --force-reinstall -r anpu-backend/requirements.txt
   ```
2. 重启 FastAPI 服务；若前端需切换接口地址，设置 `VUE_APP_API_BASE_URL` 即可。

完成所有步骤后，前端请求将指向正确端口，后端登录时也不会再触发 `bcrypt` 版本异常。***
