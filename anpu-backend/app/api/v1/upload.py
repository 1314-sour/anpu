from fastapi import APIRouter, UploadFile, File, Depends
from ...utils.response import success_response, error_response
from ...dependencies import get_current_user
from ...models.user import User
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/upload", tags=["文件上传"])

# 上传目录
UPLOAD_DIR = Path("uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传图片"""
    try:
        # 检查文件类型
        if not file.content_type.startswith('image/'):
            return error_response(400, "只能上传图片文件")
        
        # 生成唯一文件名
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = UPLOAD_DIR / filename
        
        # 保存文件
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 返回文件URL
        file_url = f"/uploads/images/{filename}"
        
        return success_response(
            data={"url": file_url, "filename": filename},
            message="上传成功"
        )
    except Exception as e:
        return error_response(500, f"上传失败: {str(e)}")
