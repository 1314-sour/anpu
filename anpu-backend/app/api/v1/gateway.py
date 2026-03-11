from fastapi import APIRouter, Security, HTTPException, status, Body
from fastapi.security import APIKeyHeader
from typing import Dict, Any

# ==========================================
# 1. 废除严格数据契约，改为动态接收 (已删除 GatewayPayload)
# ==========================================

# ==========================================
# 2. 建立机机鉴权机制 (完美保持不变)
# ==========================================
api_key_header = APIKeyHeader(name="X-Gateway-Token", auto_error=False)

def verify_gateway_token(api_key: str = Security(api_key_header)):
    VALID_TOKEN = "secret-key-123"
    if api_key != VALID_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Gateway Token",
        )
    return api_key

# ==========================================
# 3. 划定专属的路由路径
# ==========================================
router = APIRouter()

# ==========================================
# 4. 实现“照单全收”的动态接收逻辑
# ==========================================
@router.post("/upload")
async def receive_gateway_data(
    # 【核心魔法】：直接声明接收一个字典，Body(...) 告诉 FastAPI 去请求体里抓取全部 JSON
    data: Dict[str, Any] = Body(...),
    token: str = Security(verify_gateway_token)
):
    """
    专门接收物理网关推送的任意格式 JSON 数据
    """
    # 尝试提取基础字段用于打印，如果硬件没传 device_id，也不会报错，只会显示"未知设备"
    device_id = data.get("device_id", "未知设备")
    
    # 打印到控制台，肉眼确认数据已成功接住
    print("=" * 40)
    print(f"✅ 成功接收到动态网关数据!")
    print(f"📍 提取设备 ID: {device_id}")
    print(f"📦 完整原始报文: {data}")
    print("=" * 40)
    
    # 立即返回 200 OK，顺便把收到的“键名”返回给硬件，方便他们联调核对
    return {
        "status": "success", 
        "message": "Dynamic data received safely",
        "received_fields": list(data.keys()) 
    }