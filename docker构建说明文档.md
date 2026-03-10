# Docker 使用说明

本项目保持原有目录结构，仅在 `AnPu/anpu-backend/` 中加入了 `Dockerfile`、`.dockerignore` 与完善的 `requirements.txt`。该文档位于 `AnPu` 根目录，描述如何在 **不改动包结构** 的前提下利用现有文件完成镜像构建与运行。

> 以下命令默认在 `AnPu` 根目录执行；如实际路径不同，请相应替换。

---

## 1. 准备工作

1. 检查 `AnPu/anpu-backend/.env`，确保 `DATABASE_URL`、`CORS_ORIGINS` 等配置正确。  
   - 容器内部无法访问宿主的 `localhost`，如需连接宿主 MySQL，请改为 `host.docker.internal`（Windows/macOS）或宿主机实际 IP。
   - 如果继续使用默认的 SQLite (`sqlite:///./anpu.db`)，容器会在 `/app/anpu.db` 自动创建数据库文件，可按需挂载卷以持久化。
   - `CORS_ORIGINS` 必须使用英文逗号分隔多个源，且包含前端实际访问端口（如 `http://localhost:7000`）。复制文案时混入中文逗号会导致 FastAPI 返回 400，浏览器预检 `OPTIONS` 请求提示 `No 'Access-Control-Allow-Origin' header`。
   - `app/config.py` 已固定从 `anpu-backend/.env` 读取配置，无论在根目录还是子目录执行 `uvicorn`/Docker 容器都能加载最新的 `CORS_ORIGINS`，避免因为找不到 `.env` 而退回默认值（仅允许 `http://localhost:8080`）。
2. 确认 Docker Desktop（或其他 Docker 环境）已安装并运行。
3. 进入后端目录（Dockerfile 即位于此处）：

```bash
cd AnPu/anpu-backend
```

### 1.1 新增文件概览

| 文件 | 位置 | 作用 |
| --- | --- | --- |
| `Dockerfile` | `AnPu/anpu-backend/Dockerfile` | 基于 `python:3.11-slim` 安装 `requirements.txt`，复制源码并执行 `uvicorn app.main:app --host 0.0.0.0 --port 8000`，同时预创建 `uploads/images` 目录。 |
| `.dockerignore` | `AnPu/anpu-backend/.dockerignore` | 忽略 `.git`、虚拟环境、缓存、`node_modules`、`.pyc` 等无关内容，缩短构建时间。 |
| `requirements.txt` | `AnPu/anpu-backend/requirements.txt` | 固定 FastAPI、Uvicorn、SQLAlchemy、pydantic-settings、PyMySQL、bcrypt 等依赖版本，保证镜像安装一致。 |

#### Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .
RUN mkdir -p /app/uploads/images

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### .dockerignore

```text
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.venv
venv
env
build
dist
.git
.gitignore
*.log
node_modules
*.sqlite3
```

#### requirements.txt

```text
# FastAPI核心框架
fastapi==0.115.6
uvicorn[standard]==0.38.0
python-multipart==0.0.6

# 数据库
SQLAlchemy==2.0.23
pymysql==1.1.0

# 安全认证
python-jose[cryptography]==3.3.0
bcrypt==3.2.2
python-dotenv==1.0.0

# 数据验证
pydantic==2.10.6
pydantic-settings==2.7.1

# 其他依赖
email-validator==2.1.0
```

> 以上文件全部位于 `anpu-backend` 子目录，项目其它结构保持不变。

---

## 2. 构建镜像

```bash
docker build -t anpu-backend:latest .
```

- 基于 `python:3.11-slim`。
- 自动安装 `requirements.txt` 中依赖并复制现有源码。
- 生成的镜像命名为 `anpu-backend:latest`（可自行调整 tag）。

---

## 3. 运行容器

```bash
docker run -d ^
  --name anpu-backend ^
  --env-file .env ^
  -p 8000:8000 ^
  -v %cd%/uploads:/app/uploads ^
  anpu-backend:latest
```

> Windows PowerShell/CMD 使用 `^` 作为续行符；在 Linux/macOS 中将 `^` 替换为 `\`。
> Linux/macOS 示例：`docker run -d --name anpu-backend --env-file .env -p 8000:8000 -v $(pwd)/uploads:/app/uploads anpu-backend:latest`

- `--env-file .env`：加载已有环境变量，保持与本地调试一致的配置。
- `-p 8000:8000`：映射容器端口到宿主机。
- `-v ./uploads:/app/uploads`（可选）：持久化上传文件；如果不挂载，容器销毁后上传内容会丢失。
- 如果本地曾经手动安装过依赖，建议先执行 `pip install --upgrade --force-reinstall -r requirements.txt`，确保 `bcrypt` 环境一致，否则登录接口可能会因为旧的 Passlib 依赖残留而报 `error reading bcrypt version`。
- 若数据库位于宿主机，请确保 `.env` 中 `DATABASE_URL` 指向宿主可访问地址。

---

## 4. 常用操作

```bash
# 查看运行日志
docker logs -f anpu-backend

# 停止并删除容器
docker stop anpu-backend && docker rm anpu-backend

# 删除镜像（如需重建）
docker rmi anpu-backend:latest
```

如需重新部署，只需重复“构建镜像 + 运行容器”步骤；整个 `AnPu` 目录结构保持不变。

---

## 5. 前端验证

1. 容器启动后访问 `http://localhost:8000/health`，应返回 `{"status": "healthy"}`。
2. 前端仍指向 `http://localhost:8000`，无需调整接口地址。
3. 若出现“网络错误”或 5xx，请检查：
   - 容器日志：`docker logs -f anpu-backend`
   - 数据库连通性（端口、防火墙、HOST 配置）
   - `.env` 中 `CORS_ORIGINS` 是否包含前端使用的端口（7000/7002 等）

---

## 6. 前端容器化 (新增)

前端目录依旧位于 `AnPu/anpu-frontend/`，只是在该目录下新增了 `Dockerfile`、`.dockerignore` 与 `nginx.conf` 等文件，保持原有结构不变即可完成容器化。

### 6.0 新增文件概览

| 文件 | 位置 | 作用 |
| --- | --- | --- |
| `Dockerfile` | `AnPu/anpu-frontend/Dockerfile` | 多阶段构建：`--target dev` 运行 `npm run serve` 暴露 7002，默认目标会执行 `npm run build` 并将 `dist` 拷贝到 Nginx。 |
| `.dockerignore` | `AnPu/anpu-frontend/.dockerignore` | 忽略 `node_modules`、`dist`、日志、IDE 配置等，加速构建并避免无用文件进入镜像。 |
| `nginx.conf` | `AnPu/anpu-frontend/nginx.conf` | 为 SPA 提供 `try_files $uri $uri/ /index.html` 回退，解决直接访问 `/login`、`/user/*` 路由 404 的问题。 |
| `vue.config.js` | `AnPu/anpu-frontend/vue.config.js` | devServer 端口默认 7002，并允许通过 `HOST`、`PORT` 环境变量覆盖，方便容器运行。 |

#### Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:18-alpine AS dev
ARG VUE_APP_API_BASE_URL=http://localhost:8000
WORKDIR /app
ENV HOST=0.0.0.0
ENV PORT=7002
ENV VUE_APP_API_BASE_URL=${VUE_APP_API_BASE_URL}
COPY package*.json ./
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 7002
CMD ["npm", "run", "serve"]

FROM node:18-alpine AS build
ARG VUE_APP_API_BASE_URL=http://localhost:8000
WORKDIR /app
ENV VUE_APP_API_BASE_URL=${VUE_APP_API_BASE_URL}
COPY package*.json ./
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM nginx:1.25-alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### .dockerignore

```text
node_modules
dist
.git
.gitignore
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-lock.yaml
.DS_Store
.idea
.vscode
coverage
*.local
```

#### nginx.conf

```nginx
server {
    listen       80;
    server_name  _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

#### vue.config.js（节选）

```javascript
const { defineConfig } = require('@vue/cli-service')

const devServerPort = Number(process.env.PORT || 7002)
const devServerHost = process.env.HOST || '0.0.0.0'

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: devServerHost,
    port: devServerPort,
    allowedHosts: 'all'
  }
})
```

> `VUE_APP_API_BASE_URL` 默认为 `http://localhost:8000`，构建镜像时可通过 `--build-arg VUE_APP_API_BASE_URL=http://host.docker.internal:8000` 覆盖，开发容器运行时也能使用 `docker run -e VUE_APP_API_BASE_URL=...` 指向任意后端地址。
### 6.1 打包/发布模式（推荐）
默认的构建目标会先执行 `npm run build`，然后用 `nginx:alpine` 提供打包后的 `dist`：
```bash
cd AnPu/anpu-frontend
docker build -t anpu-frontend:latest .
docker run -d --name anpu-frontend -p 7002:80 anpu-frontend:latest
```
- 容器对外暴露 80 端口，示例中将宿主的 7002 映射到 80，方便保持既有访问入口。
- 查看日志：`docker logs -f anpu-frontend`
- 停止/删除：`docker stop anpu-frontend && docker rm anpu-frontend`
- 自定义 `nginx.conf` 已内置到镜像中，`location / { try_files $uri $uri/ /index.html; }` 确保像 `/login`、`/user/profile` 等 history 模式路由直接用 IP 访问时也会回落到 `index.html`，不会再出现 404。


### 6.2 开发模式 (热更新)
容器内直接执行 `npm run serve`，支持热更新调试：
```bash
cd AnPu/anpu-frontend
docker build -t anpu-frontend-dev --target dev .
docker run --rm -it --name anpu-frontend-dev -p 7002:7002 anpu-frontend-dev
```
- 基于 `node:18-alpine`，会执行 `npm ci`，与本地 lockfile 完全一致。
- `HOST`、`PORT` 默认分别是 `0.0.0.0` 与 `7002`，可在 `docker run` 时通过 `-e` 覆盖。
- 退出开发容器只需 `Ctrl+C`，镜像仍可复用。

### 6.3 登录入口与主机 IP
默认在宿主浏览器中直接访问 `http://localhost:7002/login` 即可。如果需要在其他设备/容器中访问宿主机，请用 `ipconfig` (Windows) 或 `ifconfig` (macOS/Linux) 查出 IPv4 地址，将 `localhost` 替换成对应 IP 即可。

---

通过以上新增文件即可在 Docker 容器内创建并运行前端应用，无需调整现有目录结构。

---
