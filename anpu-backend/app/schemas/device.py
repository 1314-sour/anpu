from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 设备分组 Schemas
class DeviceGroupBase(BaseModel):
    name: str
    parent_id: int = 0


class DeviceGroupCreate(DeviceGroupBase):
    pass


class DeviceGroupUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class DeviceGroupResponse(DeviceGroupBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 设备 Schemas
class DeviceBase(BaseModel):
    name: str
    status: str = 'offline'
    group_id: Optional[int] = None
    address: str = ''
    remark: str = ''
    iccid: str = ''
    sort: int = 0
    image_url: str = ''
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    coordinate_type: str = '东'
    top_order_unit: str = '默示'
    default_value_type: str = '自定义'
    default_value: str = '0'
    device_number: str = ''
    manufacture_date: Optional[str] = None
    install_date: Optional[str] = None
    warranty_years: str = ''
    warranty_unit: str = '年'
    manufacturer: str = ''


class DeviceCreate(BaseModel):
    name: str
    sn: str = ''  # SN可以为空，在网关绑定时填写
    status: str = 'offline'
    group_id: Optional[int] = None
    address: str = ''
    remark: str = ''
    iccid: str = ''
    sort: int = 0
    image_url: str = ''
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    coordinate_type: str = '东'
    top_order_unit: str = '默示'
    default_value_type: str = '自定义'
    default_value: str = '0'
    device_number: str = ''
    manufacture_date: Optional[str] = None
    install_date: Optional[str] = None
    warranty_years: str = ''
    warranty_unit: str = '年'
    manufacturer: str = ''


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    group_id: Optional[int] = None
    address: Optional[str] = None
    remark: Optional[str] = None
    iccid: Optional[str] = None
    sort: Optional[int] = None
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    coordinate_type: Optional[str] = None
    top_order_unit: Optional[str] = None
    default_value_type: Optional[str] = None
    default_value: Optional[str] = None
    device_number: Optional[str] = None
    manufacture_date: Optional[str] = None
    install_date: Optional[str] = None
    warranty_years: Optional[str] = None
    warranty_unit: Optional[str] = None
    manufacturer: Optional[str] = None


class DeviceResponse(DeviceBase):
    id: int
    creator_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
