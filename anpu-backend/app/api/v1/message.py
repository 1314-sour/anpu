from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...models.message import Message
from ...utils.response import success_response

router = APIRouter()

TYPE_MAP = {
    'reserved': '报警消息',
    'workorder': '工单消息',
    'expire': '到期提醒',
    'system': '系统公告'
}


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
