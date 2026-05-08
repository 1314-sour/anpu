from pydantic import BaseModel, ConfigDict, field_validator, model_validator
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
    model_config = ConfigDict(validate_default=True)

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

    @field_validator('address', mode='before')
    @classmethod
    def validate_address_required(cls, value):
        if value is None or str(value).strip() == '':
            raise ValueError('寄存器地址不能为空')

        text = str(value).strip()
        try:
            upper_text = text.upper()
            if upper_text.endswith('H'):
                parsed = int(upper_text[:-1], 16)
            elif upper_text.startswith('0X'):
                parsed = int(upper_text, 16)
            else:
                parsed = int(text)
        except ValueError as exc:
            raise ValueError('寄存器地址必须是有效整数地址') from exc

        if parsed <= 0:
            raise ValueError('寄存器地址必须大于0')

        return text

    @field_validator('read_write', mode='before')
    @classmethod
    def normalize_read_write(cls, value):
        read_write_map = {
            '只读': 'read',
            '只写': 'write',
            '读写': 'read_write',
        }
        return read_write_map.get(value, value or 'read')

    @model_validator(mode='after')
    def validate_write_config(self):
        allowed_read_write = {'read', 'write', 'read_write'}
        if self.read_write not in allowed_read_write:
            raise ValueError('读写类型只能是 read、write 或 read_write')

        if self.min_value is not None and self.max_value is not None and self.min_value > self.max_value:
            raise ValueError('最小值不能大于最大值')

        if self.read_write == 'read':
            self.default_value = ''

        return self


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
