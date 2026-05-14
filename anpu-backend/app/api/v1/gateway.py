from fastapi import APIRouter, Security, HTTPException, status, Body, WebSocket, WebSocketDisconnect, Request
from fastapi.security import APIKeyHeader
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime, timedelta
import json
import uuid
from ...database import get_db
from ...models.device import Device
from ...models.device import DeviceVariable
from ...models.device_variable_value import DeviceVariableLatestValue
from ...models.gateway_command import GatewayDownlinkCommand
from ...models.message import Message
from ...services.variable_value_service import upsert_latest_value
from ...services.wechat_mp_service import wechat_mp_service


ALARM_MESSAGE_WINDOW_MINUTES = 10


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


def parse_register_address(address):
    """
    将变量配置里的寄存器地址转成整数。
    兼容 1、"1"、"0001H"、"0x0001"、"40001" 这几类常见写法。
    """
    if address is None:
        return None

    text = str(address).strip()
    if not text:
        return None

    try:
        upper_text = text.upper()
        if upper_text.endswith("H"):
            return int(upper_text[:-1], 16)
        if upper_text.startswith("0X"):
            return int(upper_text, 16)
        return int(text)
    except ValueError:
        return None


def normalize_modbus_address(address: int):
    """
    将 40001/30001 这类带功能区前缀的地址归一成寄存器偏移地址。
    例如 40001 -> 1，40010 -> 10；普通地址 1/10 保持不变。
    """
    if address is None:
        return None

    text = str(address)
    if len(text) >= 5 and text[0] in {"0", "1", "3", "4"}:
        offset = address % 10000
        return offset if offset > 0 else address

    return address


def get_upload_start_address(data: Dict[str, Any]) -> int:
    """
    Modbus 读响应报文中通常没有起始寄存器地址，所以允许网关上传时携带。
    未携带时沿用当前协议约定：响应第一个寄存器对应地址 1。
    """
    for key in ("start_address", "register_start_address", "start_register", "address"):
        value = parse_register_address(data.get(key))
        if value is not None:
            return value
    return 1


def get_variable_key_name(var: DeviceVariable):
    key_name = getattr(var, "key_name", None)
    if key_name:
        return key_name
    return None


def resolve_variable_value(
    var: DeviceVariable,
    values: List[int],
    start_address: int,
):
    """
    阶段1：按变量绑定的寄存器地址动态取值。
    变量没有地址时不再用变量名硬编码猜测，避免新增变量解析错位。
    """

    address = parse_register_address(getattr(var, "address", None))
    if address is None:
        return None, "missing_address", None

    normalized_address = normalize_modbus_address(address)
    normalized_start = normalize_modbus_address(start_address)
    index = normalized_address - normalized_start

    if 0 <= index < len(values):
        return values[index], "address", {
            "address": address,
            "normalized_address": normalized_address,
            "start_address": start_address,
            "normalized_start": normalized_start,
            "index": index,
        }

    return None, "address_out_of_range", {
        "address": address,
        "normalized_address": normalized_address,
        "start_address": start_address,
        "normalized_start": normalized_start,
        "index": index,
        "value_count": len(values),
    }


def is_matched_value(match_type: str) -> bool:
    return match_type == "address"


def to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def evaluate_range_alarm(var: DeviceVariable, value):
    current = to_float(value)
    min_value = to_float(getattr(var, "min_value", None))
    max_value = to_float(getattr(var, "max_value", None))

    if current is None:
        return False, ""

    if min_value is not None and current < min_value:
        return True, f"变量{var.var_name}当前值{value}低于最小值{min_value}"

    if max_value is not None and current > max_value:
        return True, f"变量{var.var_name}当前值{value}高于最大值{max_value}"

    return False, ""


def build_range_text(var: DeviceVariable):
    min_text = getattr(var, "min_value", None)
    max_text = getattr(var, "max_value", None)
    return (
        f"{min_text if min_text is not None else '-'} ~ "
        f"{max_text if max_text is not None else '-'}"
    )


def build_alarm_content(device: Device, var: DeviceVariable, value, alarm_message: str):
    return (
        f"设备：{device.name}；"
        f"网关SN：{device.sn}；"
        f"变量：{var.var_name}；"
        f"异常值：{value}；"
        f"设定范围：{build_range_text(var)}；"
        f"寄存器地址：{getattr(var, 'address', '')}；"
        f"报警原因：{alarm_message}。"
    )


def build_error_command(
    command_id: str,
    device: Device,
    var: DeviceVariable,
    value,
    alarm_message: str,
):
    return {
        "command_id": command_id,
        "type": "variable_range_error",
        "gateway_no": device.sn,
        "device_id": device.id,
        "variable_id": var.id,
        "variable_name": var.var_name,
        "address": getattr(var, "address", None),
        "key_name": get_variable_key_name(var),
        "value": value,
        "min_value": float(var.min_value) if getattr(var, "min_value", None) is not None else None,
        "max_value": float(var.max_value) if getattr(var, "max_value", None) is not None else None,
        "message": alarm_message,
    }


def json_dumps(data: Dict[str, Any]):
    return json.dumps(data, ensure_ascii=False, default=str)


def load_command_payload(command: GatewayDownlinkCommand):
    try:
        return json.loads(command.payload)
    except (TypeError, ValueError):
        return {}


def get_existing_active_command(db: Session, gateway_no: str, variable_id: int):
    return (
        db.query(GatewayDownlinkCommand)
        .filter(
            GatewayDownlinkCommand.gateway_no == gateway_no,
            GatewayDownlinkCommand.variable_id == variable_id,
            GatewayDownlinkCommand.command_type == "variable_range_error",
            GatewayDownlinkCommand.status.in_(["pending", "sent"]),
        )
        .order_by(GatewayDownlinkCommand.id.desc())
        .first()
    )


def create_or_get_error_command(
    db: Session,
    device: Device,
    var: DeviceVariable,
    value,
    alarm_message: str,
):
    existing = get_existing_active_command(db, device.sn, var.id)
    if existing:
        return load_command_payload(existing), existing, False

    command_id = uuid.uuid4().hex
    payload = build_error_command(
        command_id=command_id,
        device=device,
        var=var,
        value=value,
        alarm_message=alarm_message,
    )
    command = GatewayDownlinkCommand(
        command_id=command_id,
        gateway_no=device.sn,
        device_id=device.id,
        variable_id=var.id,
        command_type="variable_range_error",
        payload=json_dumps(payload),
        status="pending",
    )
    db.add(command)
    return payload, command, True


def serialize_downlink_command(command: GatewayDownlinkCommand):
    payload = load_command_payload(command)
    payload.setdefault("command_id", command.command_id)
    payload.setdefault("type", command.command_type)
    payload.setdefault("gateway_no", command.gateway_no)
    payload.setdefault("device_id", command.device_id)
    payload.setdefault("variable_id", command.variable_id)
    return payload


def get_latest_value(db: Session, variable_id: int):
    return (
        db.query(DeviceVariableLatestValue)
        .filter(DeviceVariableLatestValue.variable_id == variable_id)
        .first()
    )


def build_alarm_title(device: Device, var: DeviceVariable, message_type: str):
    suffix = "变量报警" if message_type == "reserved" else "报警处理工单"
    return f"{device.name}-{var.var_name}{suffix}"


def has_recent_alarm_message(db: Session, device: Device, var: DeviceVariable, message_type: str):
    title = build_alarm_title(device, var, message_type)
    latest_message = (
        db.query(Message)
        .filter(
            Message.user_id == device.creator_id,
            Message.type == message_type,
            Message.title == title,
        )
        .order_by(Message.created_at.desc(), Message.id.desc())
        .first()
    )

    if latest_message is None:
        return False

    if latest_message.created_at is None:
        return True

    window_start = datetime.now() - timedelta(minutes=ALARM_MESSAGE_WINDOW_MINUTES)
    return latest_message.created_at >= window_start


def create_alarm_messages_if_needed(
    db: Session,
    device: Device,
    var: DeviceVariable,
    value,
    alarm_message: str,
    match_key,
    previous_data_quality: Optional[str],
):
    """
    按变量和时间窗口写消息中心和工单。
    同一变量 10 分钟内只保留一组报警/工单；超过窗口后视为一次新的报警。
    """
    records = []
    content = build_alarm_content(device, var, value, alarm_message)

    if not has_recent_alarm_message(db, device, var, "reserved"):
        alarm_message_record = Message(
            user_id=device.creator_id,
            title=build_alarm_title(device, var, "reserved"),
            content=content,
            type="reserved",
            is_read=False,
        )
        db.add(alarm_message_record)
        records.append(alarm_message_record)

    if not has_recent_alarm_message(db, device, var, "workorder"):
        workorder_message_record = Message(
            user_id=device.creator_id,
            title=build_alarm_title(device, var, "workorder"),
            content=f"请及时处理该设备变量报警。{content}",
            type="workorder",
            is_read=False,
        )
        db.add(workorder_message_record)
        records.append(workorder_message_record)

    return records


async def push_wechat_alarm_notifications(notifications: List[Dict[str, Any]]):
    if not notifications:
        return []

    results = []
    for notification in notifications:
        try:
            send_result = await wechat_mp_service.send_alarm(**notification)
            results.append({
                "title": notification.get("title"),
                "status": "sent" if send_result else "skipped",
                "result": send_result,
            })
        except Exception as e:
            print("WeChat MP alarm push failed:", e)
            results.append({
                "title": notification.get("title"),
                "status": "failed",
                "error": str(e),
            })
    return results
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
    start_address = get_upload_start_address(data)
    print("📍 本次上行起始寄存器地址:", start_address)
    print("📍 归一化起始寄存器地址:", normalize_modbus_address(start_address))

    try:
        ws_variables = []
        skipped_variables = []
        error_commands = []
        alarm_records = []
        wechat_alarm_notifications = []

        for var in variables:
            key_name = get_variable_key_name(var)
            value, match_type, match_key = resolve_variable_value(
                var=var,
                values=values,
                start_address=start_address,
            )

            if not is_matched_value(match_type):
                skipped_variables.append({
                    "id": var.id,
                    "name": var.var_name,
                    "address": getattr(var, "address", None),
                    "match_type": match_type,
                    "match_key": match_key,
                })
                print(
                    f"变量未在本次报文范围内，保留原最新值 -> id={var.id}, "
                    f"name={var.var_name}, match={match_type}:{match_key}"
                )
                continue

            is_alarm, alarm_message = evaluate_range_alarm(var, value)
            previous_latest = get_latest_value(db, var.id)
            previous_data_quality = previous_latest.data_quality if previous_latest else None

            if is_alarm:
                data_quality = "alarm"
            else:
                data_quality = "good"

            print(
                f"变量最新值入库 -> id={var.id}, "
                f"name={var.var_name}, "
                f"key_name={key_name}, "
                f"value={value}, "
                f"quality={data_quality}, "
                f"match={match_type}:{match_key}"
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
                "device_id": device.id,
                "device_name": device.name,
                "gateway_no": gateway_no,
                "variable_name": var.var_name,
                "name": var.var_name,
                "key_name": key_name,
                "address": getattr(var, "address", None),
                "value": value,
                "data_quality": data_quality,
                "is_alarm": is_alarm,
                "alarm_message": alarm_message,
                "min_value": float(var.min_value) if getattr(var, "min_value", None) is not None else None,
                "max_value": float(var.max_value) if getattr(var, "max_value", None) is not None else None,
                "match_type": match_type,
                "match_key": match_key,
            })

            if is_alarm:
                downlink_command, command_record, command_created = create_or_get_error_command(
                    db=db,
                    device=device,
                    var=var,
                    value=value,
                    alarm_message=alarm_message,
                )
                error_commands.append(downlink_command)
                alarm_messages = create_alarm_messages_if_needed(
                    db=db,
                    device=device,
                    var=var,
                    value=value,
                    alarm_message=alarm_message,
                    match_key=match_key,
                    previous_data_quality=previous_data_quality,
                )
                for alarm_record in alarm_messages:
                    alarm_records.append({
                        "variable_id": var.id,
                        "variable_name": var.var_name,
                        "message_title": alarm_record.title,
                        "message_type": alarm_record.type,
                    })
                    if alarm_record.type == "reserved":
                        wechat_alarm_notifications.append({
                            "title": alarm_record.title,
                            "content": alarm_record.content or "",
                            "device_name": device.name,
                            "variable_name": var.var_name,
                            "value": value,
                            "alarm_message": alarm_message,
                            "username": device.creator.username if device.creator else None,
                        })
                print(
                    f"下行报警命令{'创建' if command_created else '复用'} -> "
                    f"command_id={command_record.command_id}, variable_id={var.id}"
                )
            elif previous_data_quality == "alarm":
                active_command = get_existing_active_command(db, gateway_no, var.id)
                if active_command:
                    active_command.status = "cancelled"
                    active_command.ack_message = "变量恢复正常，自动取消未确认报警命令"

        db.commit()

    except Exception as e:
        db.rollback()
        print("❌ 变量最新值入库失败:", e)

        return {
            "status": "error",
            "message": f"变量最新值入库失败: {str(e)}"
        }

    # 6. 广播给前端
    wechat_push_results = await push_wechat_alarm_notifications(wechat_alarm_notifications)

    final_data = {
        "gateway_no": gateway_no,
        "device_id": device.id,
        "variables": ws_variables,
        "skipped_variables": skipped_variables,
        "alarm_records": alarm_records,
        "wechat_push_results": wechat_push_results,
        "commands": error_commands,
        "error_commands": error_commands,
    }

    print("🎯 最终广播数据:", final_data)

    await manager.broadcast(final_data)

    return {
        "status": "success",
        "message": "网关数据接收并解析成功",
        "gateway_no": gateway_no,
        "device_id": device.id,
        "received_fields": list(data.keys()),
        "start_address": start_address,
        "variables": ws_variables,
        "skipped_variables": skipped_variables,
        "alarm_records": alarm_records,
        "wechat_push_results": wechat_push_results,
        "commands": error_commands,
        "error_commands": error_commands,
    }


@router.get("/commands/pending")
async def get_pending_commands(
    gateway_no: str,
    limit: int = 20,
    token: str = Security(verify_gateway_token),
    db: Session = Depends(get_db)
):
    commands = (
        db.query(GatewayDownlinkCommand)
        .filter(
            GatewayDownlinkCommand.gateway_no == gateway_no,
            GatewayDownlinkCommand.status.in_(["pending", "sent"]),
        )
        .order_by(GatewayDownlinkCommand.id.asc())
        .limit(limit)
        .all()
    )

    result = []
    for command in commands:
        if command.status == "pending":
            command.status = "sent"
        result.append(serialize_downlink_command(command))

    db.commit()

    return {
        "status": "success",
        "gateway_no": gateway_no,
        "commands": result,
        "error_commands": result,
    }


@router.post("/commands/ack")
async def ack_gateway_command(
    data: Dict[str, Any] = Body(...),
    token: str = Security(verify_gateway_token),
    db: Session = Depends(get_db)
):
    command_id = data.get("command_id")
    gateway_no = data.get("gateway_no")
    ack_status = data.get("status") or data.get("ack_status") or "acked"
    ack_message = data.get("message") or data.get("ack_message") or ""

    if not command_id:
        return {
            "status": "error",
            "message": "缺少 command_id"
        }

    query = db.query(GatewayDownlinkCommand).filter(
        GatewayDownlinkCommand.command_id == command_id
    )
    if gateway_no:
        query = query.filter(GatewayDownlinkCommand.gateway_no == gateway_no)

    command = query.first()
    if not command:
        return {
            "status": "error",
            "message": "未找到下行命令"
        }

    allowed_status = {"acked", "failed", "cancelled"}
    command.status = ack_status if ack_status in allowed_status else "acked"
    command.ack_message = ack_message
    command.acked_at = datetime.utcnow()
    db.commit()

    await manager.broadcast({
        "type": "command_ack",
        "gateway_no": command.gateway_no,
        "command_id": command.command_id,
        "status": command.status,
        "message": command.ack_message,
    })

    return {
        "status": "success",
        "message": "命令确认已记录",
        "command_id": command.command_id,
        "command_status": command.status,
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
