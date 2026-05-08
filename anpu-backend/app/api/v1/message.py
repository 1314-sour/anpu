from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...models.message import Message
from ...models.device import Device, DeviceVariable
from ...models.device_variable_value import DeviceVariableLatestValue
from ...utils.response import success_response

router = APIRouter()

ALARM_MESSAGE_WINDOW_MINUTES = 10

TYPE_MAP = {
    'reserved': '报警消息',
    'workorder': '工单消息',
    'expire': '到期提醒',
    'system': '系统公告'
}


def build_alarm_title(device: Device, variable: DeviceVariable, message_type: str):
    suffix = "变量报警" if message_type == "reserved" else "报警处理工单"
    return f"{device.name}-{variable.var_name}{suffix}"


def has_recent_alarm_message(db: Session, user_id: int, title: str, message_type: str):
    latest_message = (
        db.query(Message)
        .filter(
            Message.user_id == user_id,
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


def sync_current_alarm_messages(db: Session, current_user: User):
    """
    将当前最新值表里的报警状态同步到消息中心。
    这个补偿用于处理：变量列表已经红色，但报警发生时未生成消息或消息写给其他用户的情况。
    """
    alarm_rows = (
        db.query(Device, DeviceVariable, DeviceVariableLatestValue)
        .join(DeviceVariable, DeviceVariable.device_id == Device.id)
        .join(DeviceVariableLatestValue, DeviceVariableLatestValue.variable_id == DeviceVariable.id)
        .filter(DeviceVariableLatestValue.data_quality == "alarm")
        .all()
    )

    created = 0
    for device, variable, latest in alarm_rows:
        alarm_title = build_alarm_title(device, variable, "reserved")
        workorder_title = build_alarm_title(device, variable, "workorder")

        if not has_recent_alarm_message(db, current_user.id, alarm_title, "reserved"):
            db.add(Message(
                user_id=current_user.id,
                title=alarm_title,
                content="",
                type="reserved",
                is_read=False,
            ))
            created += 1

        if not has_recent_alarm_message(db, current_user.id, workorder_title, "workorder"):
            db.add(Message(
                user_id=current_user.id,
                title=workorder_title,
                content="",
                type="workorder",
                is_read=False,
            ))
            created += 1

    if created:
        db.commit()


@router.get("/list")
async def get_messages(
    type: str = None,
    is_read: bool = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取消息列表"""
    sync_current_alarm_messages(db, current_user)

    query = db.query(Message).filter(Message.user_id == current_user.id)
    
    # 类型筛选
    if type and type != 'all':
        query = query.filter(Message.type == type)
    
    # 已读/未读筛选
    if is_read is not None:
        query = query.filter(Message.is_read == is_read)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    messages = query.order_by(desc(Message.created_at))\
                   .offset((page - 1) * page_size)\
                   .limit(page_size)\
                   .all()
    
    # 格式化数据
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": [
            {
                "id": msg.id,
                "title": msg.title,
                "content": msg.content,
                "type": TYPE_MAP.get(msg.type, msg.type),
                "status": "已读" if msg.is_read else "未读",
                "time": msg.created_at.strftime("%Y-%m-%d %H:%M:%S") if msg.created_at else ""
            }
            for msg in messages
        ]
    }
    
    return success_response(data=data)


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取未读消息数量"""
    count = db.query(Message).filter(
        Message.user_id == current_user.id,
        Message.is_read == False
    ).count()
    
    return success_response(data={"count": count})


@router.post("/mark-read")
async def mark_read(
    message_ids: list[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记消息为已读"""
    db.query(Message).filter(
        Message.id.in_(message_ids),
        Message.user_id == current_user.id
    ).update({
        Message.is_read: True,
        Message.read_at: datetime.now()
    }, synchronize_session=False)
    
    db.commit()
    
    return success_response(message="标记成功")


@router.post("/mark-all-read")
async def mark_all_read(
    type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """全部标记为已读"""
    query = db.query(Message).filter(
        Message.user_id == current_user.id,
        Message.is_read == False
    )
    
    if type and type != 'all':
        query = query.filter(Message.type == type)
    
    query.update({
        Message.is_read: True,
        Message.read_at: datetime.now()
    }, synchronize_session=False)
    
    db.commit()
    
    return success_response(message="全部标记为已读")


@router.post("/mark-unread")
async def mark_unread(
    message_ids: list[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记消息为未读"""
    db.query(Message).filter(
        Message.id.in_(message_ids),
        Message.user_id == current_user.id
    ).update({
        Message.is_read: False,
        Message.read_at: None
    }, synchronize_session=False)
    
    db.commit()
    
    return success_response(message="标记未读成功")


@router.delete("/delete")
async def delete_messages(
    message_ids: list[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除消息"""
    db.query(Message).filter(
        Message.id.in_(message_ids),
        Message.user_id == current_user.id
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return success_response(message="删除成功")
