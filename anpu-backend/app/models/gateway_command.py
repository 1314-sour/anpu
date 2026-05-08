from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func

from ..database import Base


class GatewayDownlinkCommand(Base):
    __tablename__ = "gateway_downlink_commands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    command_id = Column(String(64), unique=True, nullable=False, index=True)

    gateway_no = Column(String(64), nullable=False, index=True)
    device_id = Column(Integer, nullable=False, index=True)
    variable_id = Column(Integer, nullable=True, index=True)

    command_type = Column(String(64), nullable=False)
    payload = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    ack_message = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    acked_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_gateway_status", "gateway_no", "status"),
        Index("idx_variable_status", "variable_id", "status"),
    )
