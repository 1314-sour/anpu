from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, ForeignKey, DECIMAL, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class DeviceGroup(Base):
    __tablename__ = "device_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="device_groups")
    devices = relationship("Device", back_populates="group")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    sn = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(Enum('online', 'offline'), default='offline')
    group_id = Column(Integer, ForeignKey("device_groups.id"), nullable=True)
    address = Column(String(500), default='')
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    remark = Column(Text, default='')
    iccid = Column(String(50), default='')
    sort = Column(Integer, default=0)
    # 新增字段
    image_url = Column(String(500), default='')
    latitude = Column(DECIMAL(10, 6), nullable=True)
    longitude = Column(DECIMAL(10, 6), nullable=True)
    coordinate_type = Column(Enum('西', '东'), default='东')
    top_order_unit = Column(Enum('默示', '隐藏'), default='默示')
    default_value_type = Column(Enum('自定义', '集后采集值'), default='自定义')
    default_value = Column(String(100), default='0')
    device_number = Column(String(100), default='')
    manufacture_date = Column(Date, nullable=True)
    install_date = Column(Date, nullable=True)
    warranty_years = Column(String(50), default='')
    warranty_unit = Column(Enum('年', '月'), default='年')
    manufacturer = Column(String(200), default='')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 关系
    creator = relationship("User", back_populates="devices")
    group = relationship("DeviceGroup", back_populates="devices")
    config = relationship("DeviceConfig", back_populates="device", uselist=False)
    drivers = relationship("DeviceDriver", back_populates="device", cascade="all, delete-orphan")
    variables = relationship("DeviceVariable", back_populates="device", cascade="all, delete-orphan")
    reports = relationship("DeviceReport", back_populates="device", cascade="all, delete-orphan")
    alarms = relationship("DeviceAlarm", back_populates="device", cascade="all, delete-orphan")


class DeviceConfig(Base):
    __tablename__ = "device_configs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), unique=True, nullable=False)
    device_model = Column(String(100), default='')
    hardware_version = Column(String(50), default='')
    software_version = Column(String(50), default='')
    latitude = Column(DECIMAL(10, 6), nullable=True)
    longitude = Column(DECIMAL(10, 6), nullable=True)
    coordinate_type = Column(Enum('WGS84', 'GCJ02', 'BD09'), default='WGS84')
    description = Column(Text, default='')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    device = relationship("Device", back_populates="config")


class DeviceDriver(Base):
    __tablename__ = "device_drivers"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    driver_name = Column(String(100), nullable=False)
    protocol = Column(String(50), nullable=False)
    port = Column(String(50), default='')
    baud_rate = Column(Integer, nullable=True)
    data_bits = Column(Integer, default=8)
    stop_bits = Column(Integer, default=1)
    parity = Column(Enum('无校验', '奇校验', '偶校验'), default='无校验')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    device = relationship("Device", back_populates="drivers")
    variables = relationship("DeviceVariable", back_populates="driver", foreign_keys="DeviceVariable.driver_id")


class DeviceVariable(Base):
    __tablename__ = "device_variables"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    var_name = Column(String(100), nullable=False)
    description = Column(String(255), default='')
    variable_type = Column(String(20), default='device')  # device / middle / internal
    slave_address = Column(Integer, nullable=True, default=0)
    data_type = Column(String(50), nullable=False, default='UINT16')
    register_type = Column(String(50), nullable=True, default='holding_register')
    read_write = Column(String(20), nullable=False, default='read')
    address = Column(String(50), nullable=True, default='')
    key_name = Column(String(50), default='')
    driver_id = Column(Integer, ForeignKey("device_drivers.id"), nullable=True)
    driver_name = Column(String(100), default='')
    cycle_collect = Column(Integer, default=1)  # 1=开启 0=关闭
    collect_interval = Column(Integer, default=1000)  # 采集周期 ms
    collect_mode = Column(String(50), default='周期采集')
    unit = Column(String(20), default='')
    min_value = Column(DECIMAL(15, 4), nullable=True)
    max_value = Column(DECIMAL(15, 4), nullable=True)
    default_value = Column(String(100), default='')
    expression = Column(String(500), default='')
    sort_order = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    device = relationship("Device", back_populates="variables")
    driver = relationship("DeviceDriver", back_populates="variables", foreign_keys=[driver_id])


class DeviceReport(Base):
    __tablename__ = "device_reports"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    report_name = Column(String(100), nullable=False)
    report_type = Column(String(50), nullable=False)
    variable_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    device = relationship("Device", back_populates="reports")


class DeviceAlarm(Base):
    __tablename__ = "device_alarms"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    alarm_name = Column(String(100), nullable=False)
    resolution = Column(String(50), default='')
    page_type = Column(String(50), default='')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    device = relationship("Device", back_populates="alarms")
