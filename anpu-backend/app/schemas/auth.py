from pydantic import BaseModel
from typing import Optional
from .user import UserInfo


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class TokenData(BaseModel):
    """Token 数据模型"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class LoginResponse(BaseModel):
    """登录响应数据模型"""
    token: str
    refresh_token: str
    user_info: UserInfo
