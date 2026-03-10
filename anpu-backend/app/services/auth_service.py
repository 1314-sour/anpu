from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.auth import LoginRequest, LoginResponse
from ..schemas.user import UserInfo
from ..utils.security import verify_password, create_access_token, create_refresh_token
from typing import Optional


class AuthService:
    """认证服务"""
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """认证用户"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> Optional[LoginResponse]:
        """用户登录"""
        # 验证用户
        user = AuthService.authenticate_user(db, login_data.username, login_data.password)
        if not user:
            return None
        
        # 检查账号是否被禁用
        if not user.is_active:
            return None
        
        # 生成 Token
        token_data = {"sub": user.username, "user_id": user.id}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # 构建用户信息
        user_info = UserInfo(
            user_id=str(user.id),
            username=user.username,
            nickname=user.nickname or user.username,
            role=user.role,
            email=user.email or "",
            avatar=user.avatar or ""
        )
        
        return LoginResponse(
            token=access_token,
            refresh_token=refresh_token,
            user_info=user_info
        )
