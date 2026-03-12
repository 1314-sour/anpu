from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ========== 设备详细配置 ==========
class DeviceConfigBase(BaseModel):
    device_model: str = ''
    hardware_version: str = ''
    software_version: str = ''
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    coordinate_type: str = 'WGS84'
    description: str = ''


class DeviceConfigCreate(DeviceConfigBase):
    pass


class DeviceConfigUpdate(DeviceConfigBase):
    pass


class DeviceConfigResponse(DeviceConfigBase):
    id: int
    device_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 网关驱动 ==========
class DeviceDriverBase(BaseModel):
    driver_name: str
    protocol: str
    port: str = ''
    baud_rate: Optional[int] = None
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = '无校验'


class DeviceDriverCreate(DeviceDriverBase):
    pass


class DeviceDriverUpdate(DeviceDriverBase):
    pass


class DeviceDriverResponse(DeviceDriverBase):
    id: int
    device_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 设备变量 ==========
class DeviceVariableBase(BaseModel):
    var_name: str
    description: str = ''
    variable_type: str = 'device'
    slave_address: Optional[int] = 0
    data_type: str = 'UINT16'
    register_type: Optional[str] = 'holding_register'
    read_write: str = 'read'
    address: Optional[str] = ''
    key_name: str = ''
    driver_id: Optional[int] = None
    driver_name: str = ''
    cycle_collect: int = 1
    collect_interval: int = 1000
    collect_mode: str = '周期采集'
    unit: str = ''
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default_value: str = ''
    expression: str = ''
    sort_order: int = 0


class DeviceVariableCreate(DeviceVariableBase):
    pass


class DeviceVariableUpdate(DeviceVariableBase):
    pass


class DeviceVariableResponse(DeviceVariableBase):
    id: int
    device_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 历史报表 ==========
class DeviceReportBase(BaseModel):
    report_name: str
    report_type: str
    variable_count: int = 0


class DeviceReportCreate(DeviceReportBase):
    pass


class DeviceReportUpdate(DeviceReportBase):
    pass


class DeviceReportResponse(DeviceReportBase):
    id: int
    device_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 报告管理 ==========
class DeviceAlarmBase(BaseModel):
    alarm_name: str
    resolution: str = ''
    page_type: str = ''


class DeviceAlarmCreate(DeviceAlarmBase):
    pass


class DeviceAlarmUpdate(DeviceAlarmBase):
    pass


class DeviceAlarmResponse(DeviceAlarmBase):
    id: int
    device_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 批量操作 ==========
class BatchCreateVariables(BaseModel):
    variables: List[DeviceVariableCreate]


class BatchDeleteRequest(BaseModel):
    ids: List[int]
