from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ========== 用户资料 ==========
class UserProfileUpdate(BaseModel):
    """用户资料更新"""
    contact_person: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    security_question_set: Optional[bool] = None


class UserProfileResponse(BaseModel):
    """用户资料响应"""
    username: str
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_person: Optional[str] = None
    address: Optional[str] = None
    avatar: Optional[str] = None
    register_time: Optional[str] = None
    security_question_set: bool = False
    
    class Config:
        from_attributes = True


# ========== 系统设置 ==========
class UserSettingsUpdate(BaseModel):
    """系统设置更新"""
    message_types: Optional[List[str]] = None
    notify_types: Optional[List[str]] = None
    layout_type: Optional[str] = None
    kg_display: Optional[str] = None


class UserSettingsResponse(BaseModel):
    """系统设置响应"""
    message_types: List[str] = []
    notify_types: List[str] = []
    layout_type: str = '原始比例'
    kg_display: str = '列表展示'
    
    class Config:
        from_attributes = True


# ========== 操作日志 ==========
class OperationLogQuery(BaseModel):
    """操作日志查询"""
    object: Optional[str] = None
    account: Optional[str] = None
    type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    page: int = 1
    page_size: int = 10


class OperationLogResponse(BaseModel):
    """操作日志响应"""
    id: int
    account: str
    object: Optional[str] = None
    type: str
    content: Optional[str] = None
    time: str
    
    class Config:
        from_attributes = True


# ========== 意见反馈 ==========
class FeedbackCreate(BaseModel):
    """创建反馈"""
    type: str  # function, suggestion, other
    content: str


class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: int
    type: str
    content: str
    status: str
    reply: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 安全设置 ==========
class PasswordChange(BaseModel):
    """修改密码"""
    old_password: str
    new_password: str


class AvatarUpload(BaseModel):
    """头像上传"""
    avatar_url: str
