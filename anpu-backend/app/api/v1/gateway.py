from fastapi import APIRouter, Security, HTTPException, status, Body, WebSocket, WebSocketDisconnect
from fastapi.security import APIKeyHeader
from typing import Dict, Any, List

# ==========================================
# 1. 新增：WebSocket 连接管理器 (广播站)
# ==========================================
class ConnectionManager:
    def __init__(self):
        # 记录当前连接了多少个前端网页
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """将接收到的动态字典，直接转化为 JSON 广播给所有打开网页的前端"""
        for connection in self.active_connections:
            await connection.send_json(message)

# 实例化广播管理器
manager = ConnectionManager()

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
# 4. 实现“照单全收”的动态接收逻辑 + 瞬间广播
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
    
    # 【核心新增】：触发 WebSocket 广播！将接到的字典原样推给 Vue 前端
    await manager.broadcast(data)
    
    # 立即返回 200 OK，顺便把收到的“键名”返回给硬件，方便他们联调核对
    return {
        "status": "success", 
        "message": "Dynamic data received and broadcasted safely",
        "received_fields": list(data.keys()) 
    }

# ==========================================
# 5. 新增：前端 Vue 专属的 WebSocket 接入点
# ==========================================
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # 保持长连接，等待客户端主动断开
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🔌 一个前端监控页面已断开连接")