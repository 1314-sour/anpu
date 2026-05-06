from datetime import datetime
from sqlalchemy.orm import Session

from ..models.device_variable_value import DeviceVariableLatestValue


def normalize_value(value):
    """
    统一存储格式。
    None 保持 None，其他值转字符串。
    """
    if value is None:
        return None
    return str(value)


def upsert_latest_value(
    db: Session,
    device_id: int,
    variable_id: int,
    gateway_no: str,
    key_name: str | None,
    value,
    raw_value=None,
    raw_data: str | None = None,
    data_quality: str = "good",
):
    """
    更新变量最新值。
    每个 variable_id 只保留一条记录。
    """
    now = datetime.utcnow()

    latest = (
        db.query(DeviceVariableLatestValue)
        .filter(DeviceVariableLatestValue.variable_id == variable_id)
        .first()
    )

    value_str = normalize_value(value)
    raw_value_str = normalize_value(raw_value if raw_value is not None else value)

    if latest:
        latest.device_id = device_id
        latest.gateway_no = gateway_no
        latest.key_name = key_name
        latest.value = value_str
        latest.raw_value = raw_value_str
        latest.raw_data = raw_data
        latest.data_quality = data_quality
        latest.updated_at = now
    else:
        latest = DeviceVariableLatestValue(
            device_id=device_id,
            variable_id=variable_id,
            gateway_no=gateway_no,
            key_name=key_name,
            value=value_str,
            raw_value=raw_value_str,
            raw_data=raw_data,
            data_quality=data_quality,
            updated_at=now,
        )
        db.add(latest)

    return latest