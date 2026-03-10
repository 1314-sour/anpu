from pydantic import BaseModel
from typing import Optional


class UserInfo(BaseModel):
    """用户信息模型"""
    user_id: str
    username: str
    nickname: Optional[str] = None
    role: str
    email: Optional[str] = None
    avatar: str = ""
    
    class Config:
        from_attributes = True
