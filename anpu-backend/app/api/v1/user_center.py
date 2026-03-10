from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...models.user_profile import UserProfile
from ...models.user_setting import UserSetting
from ...models.operation_log import OperationLog
from ...models.feedback import UserFeedback
from ...schemas.user_center import (
    UserProfileUpdate, UserProfileResponse,
    UserSettingsUpdate, UserSettingsResponse,
    OperationLogQuery, OperationLogResponse,
    FeedbackCreate, FeedbackResponse,
    PasswordChange, AvatarUpload
)
from ...utils.response import success_response, error_response
from ...utils.security import verify_password, get_password_hash

router = APIRouter()


# ========== 基本资料 ==========
@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户资料"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    data = {
        "username": current_user.username,
        "phone": profile.phone if profile else "",
        "email": current_user.email or "",
        "contact_person": profile.contact_person if profile else "",
        "address": profile.address if profile else "",
        "avatar": current_user.avatar or "",
        "register_time": current_user.created_at.strftime("%Y-%m-%d") if current_user.created_at else "",
        "security_question_set": profile.security_question_set if profile else False
    }
    
    return success_response(data=data)


@router.put("/profile")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户资料"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        # 创建资料
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # 更新字段
    if profile_data.contact_person is not None:
        profile.contact_person = profile_data.contact_person
    if profile_data.address is not None:
        profile.address = profile_data.address
    if profile_data.phone is not None:
        profile.phone = profile_data.phone
    if profile_data.email is not None:
        current_user.email = profile_data.email
    if profile_data.security_question_set is not None:
        profile.security_question_set = profile_data.security_question_set
    
    db.commit()
    
    return success_response(message="保存成功")


# ========== 安全设置 ==========
@router.post("/security/password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.hashed_password):
        return error_response(400, "旧密码错误")
    
    # 更新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    db.refresh(current_user)  # 刷新对象
    
    return success_response(message="密码修改成功")


@router.post("/security/avatar")
async def update_avatar(
    avatar_data: AvatarUpload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新头像"""
    current_user.avatar = avatar_data.avatar_url
    db.commit()
    
    return success_response(message="头像更新成功")


# ========== 系统设置 ==========
@router.get("/settings")
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统设置"""
    settings = db.query(UserSetting).filter(UserSetting.user_id == current_user.id).first()
    
    if not settings:
        # 返回默认设置
        data = {
            "message_types": ["保留消息", "工单消息", "到期提醒", "系统公告"],
            "notify_types": ["弹窗提醒", "浏览器标签闪烁"],
            "layout_type": "原始比例",
            "kg_display": "列表展示"
        }
    else:
        data = {
            "message_types": settings.message_types or [],
            "notify_types": settings.notify_types or [],
            "layout_type": settings.layout_type,
            "kg_display": settings.kg_display
        }
    
    return success_response(data=data)


@router.put("/settings")
async def update_settings(
    settings_data: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新系统设置"""
    settings = db.query(UserSetting).filter(UserSetting.user_id == current_user.id).first()
    
    if not settings:
        settings = UserSetting(user_id=current_user.id)
        db.add(settings)
    
    # 更新字段
    if settings_data.message_types is not None:
        settings.message_types = settings_data.message_types
    if settings_data.notify_types is not None:
        settings.notify_types = settings_data.notify_types
    if settings_data.layout_type is not None:
        settings.layout_type = settings_data.layout_type
    if settings_data.kg_display is not None:
        settings.kg_display = settings_data.kg_display
    
    db.commit()
    
    return success_response(message="设置已保存")


# ========== 操作日志 ==========
@router.get("/logs")
async def get_logs(
    object: str = None,
    account: str = None,
    type: str = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取操作日志"""
    query = db.query(OperationLog).filter(OperationLog.user_id == current_user.id)
    
    # 过滤条件
    if object:
        query = query.filter(OperationLog.object.like(f"%{object}%"))
    if account:
        query = query.filter(OperationLog.account.like(f"%{account}%"))
    if type:
        query = query.filter(OperationLog.type == type)
    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date)
    
    # 分页
    total = query.count()
    logs = query.order_by(OperationLog.created_at.desc())\
                .offset((page - 1) * page_size)\
                .limit(page_size)\
                .all()
    
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": [
            {
                "id": log.id,
                "account": log.account,
                "object": log.object or "",
                "type": log.type,
                "content": log.content or "",
                "time": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else ""
            }
            for log in logs
        ]
    }
    
    return success_response(data=data)


# ========== 意见反馈 ==========
@router.post("/feedback")
async def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交反馈"""
    feedback = UserFeedback(
        user_id=current_user.id,
        type=feedback_data.type,
        content=feedback_data.content
    )
    
    db.add(feedback)
    db.commit()
    
    return success_response(message="反馈提交成功")


@router.get("/feedback")
async def get_feedbacks(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的反馈列表"""
    query = db.query(UserFeedback).filter(UserFeedback.user_id == current_user.id)
    
    total = query.count()
    feedbacks = query.order_by(UserFeedback.created_at.desc())\
                    .offset((page - 1) * page_size)\
                    .limit(page_size)\
                    .all()
    
    data = {
        "total": total,
        "list": [
            {
                "id": fb.id,
                "type": fb.type,
                "content": fb.content,
                "status": fb.status,
                "reply": fb.reply,
                "created_at": fb.created_at.strftime("%Y-%m-%d %H:%M:%S") if fb.created_at else ""
            }
            for fb in feedbacks
        ]
    }
    
    return success_response(data=data)
