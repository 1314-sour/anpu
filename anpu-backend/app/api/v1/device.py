from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import Optional
from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...models.device import Device, DeviceGroup
from ...schemas.device import DeviceCreate, DeviceUpdate, DeviceGroupCreate, DeviceGroupUpdate
from ...utils.response import success_response

router = APIRouter()


# ==================== 设备管理 ====================

# 获取设备详情
@router.get("/detail/{device_id}")
async def get_device_detail(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取设备详情"""
    device = db.query(Device, User.username).join(User, Device.creator_id == User.id).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    device_obj, creator_name = device
    
    # 获取分组名称
    group_name = ''
    if device_obj.group_id:
        group = db.query(DeviceGroup).filter(DeviceGroup.id == device_obj.group_id).first()
        if group:
            group_name = group.name
    
    return {
        "code": 200,
        "data": {
            "id": device_obj.id,
            "name": device_obj.name,
            "sn": device_obj.sn,
            "status": device_obj.status,
            "group_id": device_obj.group_id,
            "group": group_name,
            "address": device_obj.address,
            "creator": creator_name,
            "remark": device_obj.remark,
            "iccid": device_obj.iccid,
            "sort": device_obj.sort,
            "image_url": device_obj.image_url,
            "latitude": float(device_obj.latitude) if device_obj.latitude is not None else None,
            "longitude": float(device_obj.longitude) if device_obj.longitude is not None else None,
            "coordinate_type": device_obj.coordinate_type,
            "top_order_unit": device_obj.top_order_unit,
            "default_value_type": device_obj.default_value_type,
            "default_value": device_obj.default_value,
            "device_number": device_obj.device_number,
            "manufacture_date": device_obj.manufacture_date.strftime("%Y-%m-%d") if device_obj.manufacture_date else None,
            "install_date": device_obj.install_date.strftime("%Y-%m-%d") if device_obj.install_date else None,
            "warranty_years": device_obj.warranty_years,
            "warranty_unit": device_obj.warranty_unit,
            "manufacturer": device_obj.manufacturer,
            "created_at": device_obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if device_obj.created_at else None,
            "updated_at": device_obj.updated_at.strftime("%Y-%m-%d %H:%M:%S") if device_obj.updated_at else None
        }
    }


# 获取设备列表
@router.get("/list")
async def get_devices(
    search: str = "",
    status: str = "",
    group_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取设备列表"""
    query = db.query(Device, User.username).join(User, Device.creator_id == User.id)
    
    # 搜索条件
    if search:
        query = query.filter(
            or_(
                Device.name.like(f"%{search}%"),
                Device.sn.like(f"%{search}%"),
                Device.address.like(f"%{search}%"),
                Device.iccid.like(f"%{search}%"),
                Device.remark.like(f"%{search}%")
            )
        )
    
    # 状态筛选
    if status:
        query = query.filter(Device.status == status)
    
    # 分组筛选
    if group_id is not None:
        if group_id == -1:  # 未分组
            query = query.filter(Device.group_id.is_(None))
        else:
            query = query.filter(Device.group_id == group_id)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    devices = query.order_by(desc(Device.sort), desc(Device.created_at))\
                   .offset((page - 1) * page_size)\
                   .limit(page_size)\
                   .all()
    
    # 获取分组信息
    group_dict = {}
    groups = db.query(DeviceGroup).all()
    for g in groups:
        group_dict[g.id] = g.name
    
    # 格式化数据
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": [
            {
                "id": device.id,
                "name": device.name,
                "sn": device.sn,
                "status": device.status,
                "group": group_dict.get(device.group_id, "未分组"),
                "group_id": device.group_id,
                "address": device.address,
                "creator": username,
                "remark": device.remark,
                "iccid": device.iccid,
                "sort": device.sort
            }
            for device, username in devices
        ]
    }
    
    return success_response(data=data)


@router.get("/check-name")
async def check_device_name(
    name: str,
    exclude_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """检查设备名称是否已存在
    
    - **name**: 设备名称
    - **exclude_id**: 排除的设备ID（编辑时排除当前设备）
    """
    query = db.query(Device).filter(Device.name == name.strip())
    
    # 编辑模式时，排除当前设备
    if exclude_id:
        query = query.filter(Device.id != exclude_id)
    
    existing = query.first()
    
    return success_response(data={
        "exists": existing is not None,
        "message": "该名称已存在，请勿重复添加" if existing else ""
    })


@router.post("/create")
async def create_device(
    device: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建设备"""
    print(f"\n===== 创建设备 =====")
    payload = device.dict()
    payload["sn"] = payload["sn"].strip()
    print(f"接收到的数据: {payload}")

    if not payload["sn"]:
        raise HTTPException(status_code=400, detail="网关SN编号不能为空")
    
    # 检查设备名称是否已存在
    existing_name = db.query(Device).filter(Device.name == device.name.strip()).first()
    if existing_name:
        raise HTTPException(status_code=400, detail="该名称已存在，请勿重复添加")
    
    existing = db.query(Device).filter(Device.sn == payload["sn"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="SN编号已存在")
    
    new_device = Device(
        **payload,
        creator_id=current_user.id
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    
    print(f"设备创建成功, ID: {new_device.id}")
    print(f"===== 创建完成 =====\n")
    
    return success_response(message="设备创建成功", data={"id": new_device.id})


@router.put("/update/{device_id}")
async def update_device(
    device_id: int,
    device: DeviceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新设备"""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 检查设备名称是否与其他设备重复
    if device.name:
        existing_name = db.query(Device).filter(
            Device.name == device.name.strip(),
            Device.id != device_id
        ).first()
        if existing_name:
            raise HTTPException(status_code=400, detail="该名称已存在，请勿重复添加")
    
    # 更新字段
    for key, value in device.dict(exclude_unset=True).items():
        setattr(db_device, key, value)
    
    db.commit()
    
    return success_response(message="设备更新成功")


@router.delete("/delete/{device_id}")
async def delete_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除设备"""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    db.delete(db_device)
    db.commit()
    
    return success_response(message="设备删除成功")


@router.post("/batch-update-group")
async def batch_update_group(
    device_ids: list[int],
    group_id: Optional[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量更新设备分组"""
    db.query(Device).filter(Device.id.in_(device_ids)).update(
        {Device.group_id: group_id},
        synchronize_session=False
    )
    db.commit()
    
    return success_response(message="批量更新成功")


# ==================== 分组管理 ====================

@router.get("/groups/list")
async def get_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分组列表（树形结构）"""
    groups = db.query(DeviceGroup).filter(DeviceGroup.user_id == current_user.id).all()
    
    # 构建树形结构
    group_dict = {}
    for g in groups:
        group_dict[g.id] = {
            "id": g.id,
            "label": g.name,
            "parent_id": g.parent_id,
            "children": []
        }
    
    # 组织树形结构
    tree = []
    for g in group_dict.values():
        if g["parent_id"] == 0:
            tree.append(g)
        else:
            parent = group_dict.get(g["parent_id"])
            if parent:
                parent["children"].append(g)
    
    return success_response(data=tree)


@router.post("/groups/create")
async def create_group(
    group: DeviceGroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建分组"""
    new_group = DeviceGroup(
        **group.dict(),
        user_id=current_user.id
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    return success_response(message="分组创建成功", data={"id": new_group.id})


@router.put("/groups/update/{group_id}")
async def update_group(
    group_id: int,
    group: DeviceGroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新分组"""
    db_group = db.query(DeviceGroup).filter(
        DeviceGroup.id == group_id,
        DeviceGroup.user_id == current_user.id
    ).first()
    
    if not db_group:
        raise HTTPException(status_code=404, detail="分组不存在")
    
    for key, value in group.dict(exclude_unset=True).items():
        setattr(db_group, key, value)
    
    db.commit()
    
    return success_response(message="分组更新成功")


@router.delete("/groups/delete/{group_id}")
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除分组"""
    db_group = db.query(DeviceGroup).filter(
        DeviceGroup.id == group_id,
        DeviceGroup.user_id == current_user.id
    ).first()
    
    if not db_group:
        raise HTTPException(status_code=404, detail="分组不存在")
    
    # 检查是否有设备
    device_count = db.query(Device).filter(Device.group_id == group_id).count()
    if device_count > 0:
        raise HTTPException(status_code=400, detail=f"该分组下还有{device_count}个设备，无法删除")
    
    db.delete(db_group)
    db.commit()
    
    return success_response(message="分组删除成功")


@router.get("/groups/{group_id}/devices")
async def get_group_devices(
    group_id: int,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分组下的设备"""
    query = db.query(Device, User.username).join(User, Device.creator_id == User.id)
    
    if group_id == -1:  # 未分组
        query = query.filter(Device.group_id.is_(None))
    else:
        query = query.filter(Device.group_id == group_id)
    
    # 搜索
    if search:
        query = query.filter(
            or_(
                Device.name.like(f"%{search}%"),
                Device.sn.like(f"%{search}%"),
                Device.address.like(f"%{search}%")
            )
        )
    
    total = query.count()
    
    devices = query.order_by(desc(Device.created_at))\
                   .offset((page - 1) * page_size)\
                   .limit(page_size)\
                   .all()
    
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": [
            {
                "id": device.id,
                "name": device.name,
                "sn": device.sn,
                "status": "在线" if device.status == "online" else "离线",
                "address": device.address,
                "creator": username
            }
            for device, username in devices
        ]
    }
    
    return success_response(data=data)


@router.post("/groups/{group_id}/remove-devices")
async def remove_devices_from_group(
    group_id: int,
    device_ids: list[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从分组中移除设备"""
    db.query(Device).filter(
        Device.id.in_(device_ids),
        Device.group_id == group_id
    ).update({Device.group_id: None}, synchronize_session=False)
    
    db.commit()
    
    return success_response(message="移出分组成功")
