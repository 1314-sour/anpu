from typing import Any, Optional
from ..schemas.common import Response


def success_response(data: Any = None, message: str = "操作成功") -> dict:
    """成功响应"""
    return Response(code=200, message=message, data=data).model_dump()


def error_response(code: int, message: str, data: Any = None) -> dict:
    """错误响应"""
    return Response(code=code, message=message, data=data).model_dump()
