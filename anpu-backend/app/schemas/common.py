from pydantic import BaseModel
from typing import Any, Optional


class Response(BaseModel):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
