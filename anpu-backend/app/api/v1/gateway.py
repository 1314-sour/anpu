from fastapi import APIRouter, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, Any

# ==========================================
# 1. 敲定严谨的数据契约 (防腐层)
# ==========================================
class GatewayPayload(BaseModel):
    device_id: str
    timestamp: int
    payload: Dict[str, Any]  # 接收任意键值对的传感器数据

# ==========================================
# 2. 建立机机鉴权机制
# ==========================================
# 定义专属的 HTTP Header 校验规则
api_key_header = APIKeyHeader(name="X-Gateway-Token", auto_error=False)

def verify_gateway_token(api_key: str = Security(api_key_header)):
    # 设定一个合法的网关测试密钥
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
# 4. 实现最简化的接收逻辑
# ==========================================
@router.post("/upload")
async def receive_gateway_data(
    data: GatewayPayload, 
    token: str = Security(verify_gateway_token) # 注入独立鉴权
):
    """
    专门接收物理网关推送的 JSON 数据
    """
    # 打印到控制台，肉眼确认数据已成功接住
    print("=" * 40)
    print(f"✅ 成功接收到网关数据!")
    print(f"设备 ID: {data.device_id}")
    print(f"时间戳: {data.timestamp}")
    print(f"核心数据: {data.payload}")
    print("=" * 40)
    
    # 立即返回 200 OK，不阻塞网关
    return {"status": "success", "message": "Data received safely"}