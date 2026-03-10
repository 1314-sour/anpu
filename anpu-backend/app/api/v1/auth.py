from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...database import get_db
from ...schemas.auth import LoginRequest
from ...services.auth_service import AuthService
from ...utils.response import success_response, error_response

router = APIRouter()


@router.post("/login")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - **username**: 用户账号
    - **password**: 用户密码
    """
    # 调用认证服务
    result = AuthService.login(db, login_data)
    
    if not result:
        return error_response(401, "用户名或密码错误")
    
    return success_response(
        data=result.model_dump(),
        message="登录成功"
    )


@router.post("/logout")
async def logout():
    """
    用户登出
    """
    # 这里可以实现 token 黑名单等逻辑
    return success_response(message="退出成功")
