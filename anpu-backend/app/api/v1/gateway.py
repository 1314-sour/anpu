from fastapi import APIRouter, Security, HTTPException, status, Body, WebSocket, WebSocketDisconnect, Request
from fastapi.security import APIKeyHeader
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import Depends
from ...database import get_db
from ...services.message_parser import parse_hex_data
from ...models.device import Device
from ...models.device import DeviceVariable

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

def verify_gateway_token(request: Request,api_key: str = Security(api_key_header)):
    VALID_TOKEN = "secret-key-123"
    print("HEADERS =", dict(request.headers))
    print("RAW api_key =", repr(api_key))
    print("EXPECTED =", repr(VALID_TOKEN))
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
    request: Request,
    data: Dict[str, Any] = Body(...),
    token: str = Security(verify_gateway_token),
    db: Session = Depends(get_db)
):
    print("HEADERS =", dict(request.headers))
    print("=" * 40)
    print("✅ 成功接收到动态网关数据!")
    print("📦 完整原始报文:", data)
    print("=" * 40)

    # 1. 取网关编号
    gateway_no = data.get("gateway_no")
    raw_hex = data.get("data")

    if not gateway_no:
        return {
            "status": "error",
            "message": "缺少 gateway_no"
        }

    if not raw_hex:
        return {
            "status": "error",
            "message": "缺少 data"
        }

    # 2. 根据 gateway_no 查设备
    device = db.query(Device).filter(Device.sn == gateway_no).first()
    # 如果你系统里网关编号存的不是 sn，而是别的字段，比如 address/name，就把这里改掉

    if not device:
        return {
            "status": "error",
            "message": f"未找到与 gateway_no={gateway_no} 绑定的设备"
        }

    device_id = device.id

    # 3. 查询该设备的变量定义
    variables = (
        db.query(DeviceVariable)
        .filter(DeviceVariable.device_id == device_id)
        .order_by(DeviceVariable.sort_order.desc(), DeviceVariable.id)
        .all()
    )

    # 4. 解析报文
    values = parse_hex_data(raw_hex)
    print("🔍 解析后的寄存器值:", values)

    # 5. 将解析结果按顺序映射到变量字段
    mapped_variables = []
    for i, var in enumerate(variables):
        value = values[i] if i < len(values) else None

        mapped_variables.append({
            "id": var.id,
            "name": var.var_name,
            "register_address": var.address,
            "data_type": var.data_type,
            "register_type": var.register_type,
            "read_write": var.read_write,
            "unit": getattr(var, "unit", ""),
            "value": value
        })

    # 6. 组织最终广播数据
    final_data = {
        "gateway_no": gateway_no,
        "device_id": device_id,
        "device_name": device.name,
        "raw_data": raw_hex,
        "variables": mapped_variables
    }

    print("🎯 最终推送前端的数据:", final_data)

    # 7. 广播给前端
    await manager.broadcast(final_data)

    return {
        "status": "success",
        "message": "网关数据接收并解析成功",
        "gateway_no": gateway_no,
        "device_id": device_id,
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