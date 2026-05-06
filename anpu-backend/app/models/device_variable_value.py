from sqlalchemy import Column, BigInteger, String, Text, DateTime, Index, UniqueConstraint
from datetime import datetime

from ..database import Base


class DeviceVariableLatestValue(Base):
    __tablename__ = "device_variable_latest_values"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    device_id = Column(BigInteger, nullable=False, index=True)
    variable_id = Column(BigInteger, nullable=False, index=True)
    gateway_no = Column(String(64), nullable=False, index=True)
    key_name = Column(String(64), nullable=True, index=True)

    value = Column(String(255), nullable=True)
    raw_value = Column(String(255), nullable=True)
    raw_data = Column(Text, nullable=True)

    data_quality = Column(String(32), nullable=False, default="good")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("variable_id", name="uk_variable_id"),
        Index("idx_device_id", "device_id"),
        Index("idx_gateway_no", "gateway_no"),
        Index("idx_key_name", "key_name"),
        Index("idx_updated_at", "updated_at"),
    )