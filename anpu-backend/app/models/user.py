from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


# 角色常量定义
class UserRole:
    """用户角色常量"""
    SUPER_ADMIN = "super_admin"          # 超级管理员
    ANPU_STAFF = "anpu_staff"            # 安普员工
    ENTERPRISE_ADMIN = "enterprise_admin" # 企业管理员
    ENTERPRISE_STAFF = "enterprise_staff" # 企业员工
    
    # 所有有效角色列表
    ALL_ROLES = [SUPER_ADMIN, ANPU_STAFF, ENTERPRISE_ADMIN, ENTERPRISE_STAFF]
    
    # 角色中文名称映射
    ROLE_NAMES = {
        SUPER_ADMIN: "超级管理员",
        ANPU_STAFF: "安普员工",
        ENTERPRISE_ADMIN: "企业管理员",
        ENTERPRISE_STAFF: "企业员工",
    }
    
    # 管理员角色（具有管理权限的角色）
    ADMIN_ROLES = [SUPER_ADMIN, ANPU_STAFF, ENTERPRISE_ADMIN]
    
    # 安普内部角色
    ANPU_ROLES = [SUPER_ADMIN, ANPU_STAFF]
    
    # 企业角色
    ENTERPRISE_ROLES = [ENTERPRISE_ADMIN, ENTERPRISE_STAFF]


class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    nickname = Column(String(50))
    # 角色: super_admin(超级管理员), anpu_staff(安普员工), enterprise_admin(企业管理员), enterprise_staff(企业员工)
    role = Column(String(30), default=UserRole.ENTERPRISE_STAFF)
    avatar = Column(String(255), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    device_groups = relationship("DeviceGroup", back_populates="user")
    devices = relationship("Device", back_populates="creator")
