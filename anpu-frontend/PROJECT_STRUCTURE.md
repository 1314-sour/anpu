# 安普物联网云平台前端项目开发文档

本文档详细说明了项目的目录结构及各核心文件的用途，帮助开发者快速上手。

## 1. 目录结构概览

```
src/
├── assets/                # 静态资源目录
│   ├── anpu-logo.png      # 平台 Logo 图片
│   └── login-background.jpg # 登录页背景图片
├── components/            # 全局公共组件目录 (目前为空，可存放通用组件)
├── router/                # 路由配置目录
│   └── index.js           # 路由定义与配置
├── views/                 # 页面视图目录
│   ├── Home/              # 首页模块 (登录后默认展示)
│   │   └── index.vue      # 首页内容组件
│   ├── Layout/            # 布局模块 (包含顶部导航的父级容器)
│   │   ├── components/    # 布局专用组件
│   │   │   └── Navbar.vue # 顶部固定导航栏组件
│   │   └── index.vue      # 主布局容器组件
│   └── Login/             # 登录页模块
│       └── index.vue      # 登录页面组件
├── App.vue                # 应用根组件
└── main.js                # 项目入口文件
```

## 2. 核心文件说明

### 入口与配置

*   **`src/main.js`**
    *   **作用**: Vue 项目的入口文件。
    *   **主要逻辑**: 初始化 Vue 实例，引入 Element UI 组件库，挂载路由 (Router)，并将应用挂载到 DOM 节点 `#app` 上。

*   **`src/App.vue`**
    *   **作用**: 应用的根组件。
    *   **主要逻辑**: 仅包含 `<router-view/>`，作为所有页面的顶级渲染出口。同时定义了全局的基础样式（如重置 `body` 的 margin/padding）。

*   **`src/router/index.js`**
    *   **作用**: 路由配置文件。
    *   **主要逻辑**:
        *   定义了 `/login` (登录页) 和 `/` (主布局) 两个一级路由。
        *   配置 `/` 重定向到 `/home`。
        *   配置 `/home` 作为主布局的子路由，实现嵌套路由结构。

### 视图模块 (Views)

#### Login (登录)
*   **`src/views/Login/index.vue`**
    *   **作用**: 用户登录页面。
    *   **主要逻辑**:
        *   展示全屏背景图和登录卡片。
        *   包含用户名、密码输入框及登录按钮。
        *   实现了基础的表单验证逻辑，验证通过后跳转至首页。
        *   **模拟权限逻辑**: 若用户名为 "admin" (包含 admin 即可)，则将角色标记为管理员并存入本地存储，用于后续控制导航栏显示。

#### Layout (布局)
*   **`src/views/Layout/index.vue`**
    *   **作用**: 系统主布局容器。
    *   **主要逻辑**:
        *   采用“上-下”结构。
        *   顶部固定放置 `Navbar` 组件。
        *   下方 `main-container` 区域使用 `<router-view />` 渲染子页面内容（如首页）。
        *   包含页面切换的过渡动画 (`transition`)。

*   **`src/views/Layout/components/Navbar.vue`**
    *   **作用**: 顶部导航栏组件。
    *   **主要逻辑**:
        *   **左侧区域**: Logo 和平台名称展示。
        *   **中间区域**: 业务功能导航。
            *   **设备监控**: 下拉包含“GM列表”、“GM分组”、“运营中心”等。
            *   **数据汇总**: 下拉包含“数据中心”。
            *   **设备地图**: 单一入口，无下拉。
            *   **后台管理**: 仅当登录角色为管理员 (`admin`) 时显示。
        *   **右侧区域**:
            *   **消息通知**: 带数字徽标的“消息”入口。
            *   **用户中心**: 显示当前登录用户名（支持动态配置），下拉包含“安全设置”、“基本资料”、“系统设置”、“操作日志”、“意见反馈”及“退出登录”。

#### Home (首页)
*   **`src/views/Home/index.vue`**
    *   **作用**: 登录后的默认展示页面。
    *   **主要逻辑**: 目前展示一个“空状态”占位图，表示尚未创建任何项目。后续可在此处添加仪表盘、统计图表等业务内容。

#### UserCenter (用户中心)
*   **`src/views/UserCenter/index.vue`**
    *   **作用**: 用户中心模块的布局容器。
    *   **主要逻辑**: 包含左侧侧边栏导航和右侧内容区。左侧菜单对应安全设置、基本资料等子页面。

*   **`src/views/UserCenter/Security.vue`**
    *   **作用**: 安全设置页面，展示头像、安全等级及修改密码等入口。
    *   **主要逻辑**:
        *   实现了头像上传功能（支持本地上传预览）。
        *   点击头像悬浮层触发弹窗，包含“本地上传”和“系统头像”两个标签页。
        *   **安全列表**: 展示登录密码、手机绑定、邮箱绑定、密保问题四个设置项，并动态显示“已设置/未设置”状态及对应图标。

*   **`src/views/UserCenter/Profile.vue`**
    *   **作用**: 基本资料页面，提供用户信息的查看与编辑表单。

*   **`src/views/UserCenter/System.vue`**
    *   **作用**: 系统设置页面，包含消息接收类型、通知方式等配置项。

*   **`src/views/UserCenter/Logs.vue`**
    *   **作用**: 操作日志页面，提供日志查询与列表展示。

*   **`src/views/UserCenter/Feedback.vue`**
    *   **作用**: 意见反馈页面，提供建议提交表单。

#### MessageCenter (消息中心)
*   **`src/views/MessageCenter/index.vue`**
    *   **作用**: 消息中心模块的布局容器。
    *   **主要逻辑**: 左侧侧边栏导航（全部/已读/未读），未读消息带红色数字徽标。

*   **`src/views/MessageCenter/AllMessages.vue`**
    *   **作用**: 全部消息列表页。
    *   **主要逻辑**: 展示所有类型的消息，支持分页、全选、标记已读/删除。

*   **`src/views/MessageCenter/ReadMessages.vue`**
    *   **作用**: 已读消息列表页。

*   **`src/views/MessageCenter/UnreadMessages.vue`**
    *   **作用**: 未读消息列表页。

#### Admin (后台管理)
*   **`src/views/Admin/index.vue`**
    *   **作用**: 后台管理模块的布局容器。
    *   **主要逻辑**: 采用左侧深色侧边栏布局，包含设备中心、数据汇总、GM中心、账号管理等子菜单。

*   **`src/views/Admin/DeviceList.vue`**
    *   **作用**: 设备管理页面。
    *   **主要逻辑**: 展示设备列表，支持搜索、状态过滤、分组过滤、自动刷新等功能，提供导入、新增及设备操作入口。

*   **`src/views/Admin/GroupList.vue`**
    *   **作用**: 分组管理页面。
    *   **主要逻辑**: 左侧展示分组树，右侧展示选中分组下的设备列表，支持添加预分组和移出分组操作。

*   **`src/views/Admin/DataSummary.vue`**
    *   **作用**: 数据汇总中心（开发中）。

*   **`src/views/Admin/GMCenter.vue`**
    *   **作用**: GM管理中心（开发中）。

*   **`src/views/Admin/AccountList.vue`**
    *   **作用**: 账号管理列表（开发中）。

## 3. 开发规范建议

1.  **新建页面**:
    *   在 `src/views` 下新建文件夹（如 `Device/`）。
    *   在其中创建 `index.vue`。
    *   在 `src/router/index.js` 的 `children` 数组中添加对应路由。

2.  **静态资源**:
    *   图片统一放入 `src/assets` 目录。
    *   引用方式: JS/HTML 中使用 `@/assets/filename.ext`。

3.  **组件命名**:
    *   文件名推荐使用 PascalCase (如 `MyComponent.vue`)。
    *   组件 `name` 属性推荐使用多单词组合 (如 `HomeView`, `TopNavbar`) 以符合 ESLint 规范。
