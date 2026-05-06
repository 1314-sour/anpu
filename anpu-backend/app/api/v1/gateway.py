from fastapi import APIRouter, Security, HTTPException, status, Body, WebSocket, WebSocketDisconnect, Request
from ...core.protocol_map import build_parsed_map
from fastapi.security import APIKeyHeader
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import Depends
from ...database import get_db
from ...models.device import Device
from ...models.device import DeviceVariable
from fastapi import Depends
from ...core.protocol_map import build_parsed_map, NAME_KEY_MAP
from ...services.variable_value_service import upsert_latest_value


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
        print(f"✅ WebSocket已连接，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"🔌 WebSocket已断开，当前连接数: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        print(f"📡 当前前端连接数: {len(self.active_connections)}")
        print(f"📡 即将广播消息: {message}")

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                print("✅ 已发送到一个前端连接")
            except Exception as e:
                print("❌ 发送失败:", e)

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



def parse_hex_data(hex_str: str):
    """
    解析类似 01030E00130000004600000001000100A225
    返回 [19, 0, 70, 0, 1, 1, 162]
    """
    try:
        hex_str = hex_str.strip()

        if len(hex_str) < 10:
            return []

        # 去掉前3字节（地址+功能码+长度）和最后2字节CRC
        payload = hex_str[6:-4]

        values = []
        for i in range(0, len(payload), 4):
            chunk = payload[i:i + 4]
            if len(chunk) == 4:
                values.append(int(chunk, 16))

        return values
    except Exception as e:
        print("❌ 报文解析失败:", e)
        return []
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

    # 1. 取网关编号和原始报文
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

    # 2. 根据 gateway_no 找设备
    # 这里默认用 Device.sn 存网关编号
    device = db.query(Device).filter(Device.sn == gateway_no).first()

    if not device:
        return {
            "status": "error",
            "message": f"未找到与 gateway_no={gateway_no} 对应的设备"
        }

    # 3. 查询该设备的变量定义
    variables = (
        db.query(DeviceVariable)
        .filter(DeviceVariable.device_id == device.id)
        .order_by(DeviceVariable.sort_order.desc(), DeviceVariable.id)
        .all()
    )

    # 4. 解析报文
    values = parse_hex_data(raw_hex)
    print("🔍 解析后的值:", values)
    parsed_map = build_parsed_map(values)
    print("🧩 协议字段解析结果:", parsed_map)

    try:
        ws_variables = []

        for var in variables:
            key_name = getattr(var, "key_name", None)

            # 兼容旧变量：如果数据库里没有 key_name，则按变量名称兜底匹配
            if not key_name:
                key_name = NAME_KEY_MAP.get((var.var_name or "").strip())

            value = parsed_map.get(key_name) if key_name else None
            data_quality = "good" if value is not None else "null"

            print(
                f"变量最新值入库 -> id={var.id}, "
                f"name={var.var_name}, "
                f"key_name={key_name}, "
                f"value={value}, "
                f"quality={data_quality}"
            )

            # 写入/更新变量最新值表
            upsert_latest_value(
                db=db,
                device_id=device.id,
                variable_id=var.id,
                gateway_no=gateway_no,
                key_name=key_name,
                value=value,
                raw_value=value,
                raw_data=raw_hex,
                data_quality=data_quality,
            )

            # WebSocket 推送给前端的数据
            ws_variables.append({
                "id": var.id,
                "key_name": key_name,
                "value": value
            })

        db.commit()

    except Exception as e:
        db.rollback()
        print("❌ 变量最新值入库失败:", e)

        return {
            "status": "error",
            "message": f"变量最新值入库失败: {str(e)}"
        }

    # 6. 广播给前端
    final_data = {
        "gateway_no": gateway_no,
        "device_id": device.id,
        "variables": ws_variables
    }

    print("🎯 最终广播数据:", final_data)

    await manager.broadcast(final_data)

    return {
        "status": "success",
        "message": "网关数据接收并解析成功",
        "gateway_no": gateway_no,
        "device_id": device.id,
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