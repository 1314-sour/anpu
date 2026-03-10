from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class UserSetting(Base):
    """用户系统设置模型"""
    
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    message_types = Column(JSON)
    notify_types = Column(JSON)
    layout_type = Column(String(20), default='原始比例')
    kg_display = Column(String(20), default='列表展示')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
