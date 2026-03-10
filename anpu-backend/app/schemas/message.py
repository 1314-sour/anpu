from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageQuery(BaseModel):
    """消息查询参数"""
    type: Optional[str] = None  # reserved, workorder, expire, system, all
    is_read: Optional[bool] = None
    page: int = 1
    page_size: int = 10


class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    title: str
    content: Optional[str] = None
    type: str
    is_read: bool
    created_at: str
    read_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class MessageMarkRead(BaseModel):
    """标记已读"""
    message_ids: list[int]


class MessageDelete(BaseModel):
    """删除消息"""
    message_ids: list[int]
