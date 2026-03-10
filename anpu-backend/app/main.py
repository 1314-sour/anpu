from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import engine, Base
from .api.v1 import auth, user_center, message, device, device_detail, upload,gateway
import os

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="安普物联网云平台后端API"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(user_center.router, prefix="/api/v1/user", tags=["用户中心"])
app.include_router(message.router, prefix="/api/v1/message", tags=["消息中心"])
app.include_router(device.router, prefix="/api/v1/device", tags=["设备管理"])
app.include_router(device_detail.router, prefix="/api/v1", tags=["设备详情"])
app.include_router(upload.router, prefix="/api/v1", tags=["文件上传"])
app.include_router(gateway.router, prefix="/api/v1/gateway", tags=["网关接入"])

# 静态文件服务
os.makedirs("uploads/images", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
