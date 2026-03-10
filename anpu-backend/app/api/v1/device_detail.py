from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...dependencies import get_current_user
from ...models.user import User
from ...models.device import DeviceConfig, DeviceDriver, DeviceVariable, DeviceReport, DeviceAlarm, Device
from ...schemas.device_detail import (
    DeviceConfigCreate, DeviceConfigUpdate, DeviceConfigResponse,
    DeviceDriverCreate, DeviceDriverUpdate, DeviceDriverResponse,
    DeviceVariableCreate, DeviceVariableUpdate, DeviceVariableResponse,
    DeviceReportCreate, DeviceReportUpdate, DeviceReportResponse,
    DeviceAlarmCreate, DeviceAlarmUpdate, DeviceAlarmResponse,
    BatchCreateVariables, BatchDeleteRequest
)

# 设备详情管理
from ...utils.response import success_response

router = APIRouter(prefix="/device-detail", tags=["设备详情管理"])


# ========== 设备详细配置 ==========
@router.get("/{device_id}/config", response_model=DeviceConfigResponse)
async def get_device_config(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取设备详细配置"""
    config = db.query(DeviceConfig).filter(DeviceConfig.device_id == device_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="设备配置不存在")
    return config


@router.post("/{device_id}/config", response_model=DeviceConfigResponse)
async def create_device_config(
    device_id: int,
    config_data: DeviceConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建设备详细配置"""
    # 检查设备是否存在
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 检查是否已存在配置
    existing = db.query(DeviceConfig).filter(DeviceConfig.device_id == device_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="设备配置已存在")
    
    config = DeviceConfig(device_id=device_id, **config_data.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.put("/{device_id}/config", response_model=DeviceConfigResponse)
async def update_device_config(
    device_id: int,
    config_data: DeviceConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新设备详细配置"""
    config = db.query(DeviceConfig).filter(DeviceConfig.device_id == device_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="设备配置不存在")
    
    for key, value in config_data.model_dump().items():
        setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    return config


# ========== 网关驱动管理 ==========
@router.get("/{device_id}/drivers")
async def get_device_drivers(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取设备驱动列表"""
    drivers = db.query(DeviceDriver).filter(DeviceDriver.device_id == device_id).all()
    return success_response(data=[{
        "id": d.id,
        "device_id": d.device_id,
        "driver_name": d.driver_name,
        "protocol": d.protocol,
        "port": d.port,
        "baud_rate": d.baud_rate,
        "data_bits": d.data_bits,
        "stop_bits": d.stop_bits,
        "parity": d.parity
    } for d in drivers])


@router.post("/{device_id}/drivers", response_model=DeviceDriverResponse)
async def create_device_driver(
    device_id: int,
    driver_data: DeviceDriverCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建设备驱动"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    driver = DeviceDriver(device_id=device_id, **driver_data.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.put("/{device_id}/drivers/{driver_id}", response_model=DeviceDriverResponse)
async def update_device_driver(
    device_id: int,
    driver_id: int,
    driver_data: DeviceDriverUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新设备驱动"""
    driver = db.query(DeviceDriver).filter(
        DeviceDriver.id == driver_id,
        DeviceDriver.device_id == device_id
    ).first()
    if not driver:
        raise HTTPException(status_code=404, detail="驱动不存在")
    
    for key, value in driver_data.model_dump().items():
        setattr(driver, key, value)
    
    db.commit()
    db.refresh(driver)
    return driver


@router.delete("/{device_id}/drivers/{driver_id}")
async def delete_device_driver(
    device_id: int,
    driver_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除设备驱动"""
    driver = db.query(DeviceDriver).filter(
        DeviceDriver.id == driver_id,
        DeviceDriver.device_id == device_id
    ).first()
    if not driver:
        raise HTTPException(status_code=404, detail="驱动不存在")
    
    db.delete(driver)
    db.commit()
    return {"code": 200, "message": "删除成功"}


# ========== 设备变量管理 ==========
@router.get("/{device_id}/variables")
async def get_device_variables(
    device_id: int,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取设备变量列表"""
    query = db.query(DeviceVariable).filter(DeviceVariable.device_id == device_id)
    query = query.order_by(DeviceVariable.sort_order.desc(), DeviceVariable.id)
    
    offset = (page - 1) * page_size
    variables = query.offset(offset).limit(page_size).all()
    total = query.count()
    
    return success_response(data=[{
        "id": v.id,
        "device_id": v.device_id,
        "var_name": v.var_name,
        "slave_address": v.slave_address,
        "data_type": v.data_type,
        "register_type": v.register_type,
        "read_write": v.read_write,
        "address": v.address,
        "key_name": v.key_name,
        "driver_name": v.driver_name,
        "collect_mode": v.collect_mode,
        "sort_order": v.sort_order
    } for v in variables])


@router.post("/{device_id}/variables", response_model=DeviceVariableResponse)
async def create_device_variable(
    device_id: int,
    variable_data: DeviceVariableCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建单个设备变量"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    variable = DeviceVariable(device_id=device_id, **variable_data.model_dump())
    db.add(variable)
    db.commit()
    db.refresh(variable)
    return variable


@router.post("/{device_id}/variables/batch")
async def batch_create_variables(
    device_id: int,
    batch_data: BatchCreateVariables,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量创建设备变量"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    variables = []
    for var_data in batch_data.variables:
        variable = DeviceVariable(device_id=device_id, **var_data.model_dump())
        db.add(variable)
        variables.append(variable)
    
    db.commit()
    return {"code": 200, "message": f"成功创建{len(variables)}个变量"}


@router.put("/{device_id}/variables/{variable_id}", response_model=DeviceVariableResponse)
async def update_device_variable(
    device_id: int,
    variable_id: int,
    variable_data: DeviceVariableUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新设备变量"""
    variable = db.query(DeviceVariable).filter(
        DeviceVariable.id == variable_id,
        DeviceVariable.device_id == device_id
    ).first()
    if not variable:
        raise HTTPException(status_code=404, detail="变量不存在")
    
    for key, value in variable_data.model_dump().items():
        setattr(variable, key, value)
    
    db.commit()
    db.refresh(variable)
    return variable


@router.delete("/{device_id}/variables")
async def batch_delete_variables(
    device_id: int,
    delete_data: BatchDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量删除设备变量"""
    deleted = db.query(DeviceVariable).filter(
        DeviceVariable.device_id == device_id,
        DeviceVariable.id.in_(delete_data.ids)
    ).delete(synchronize_session=False)
    
    db.commit()
    return {"code": 200, "message": f"成功删除{deleted}个变量"}


# ========== 历史报表管理 ==========
@router.get("/{device_id}/reports")
async def get_device_reports(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取设备报表列表"""
    reports = db.query(DeviceReport).filter(DeviceReport.device_id == device_id).all()
    return success_response(data=[{
        "id": r.id,
        "device_id": r.device_id,
        "report_name": r.report_name,
        "report_type": r.report_type,
        "variable_count": r.variable_count
    } for r in reports])


@router.post("/{device_id}/reports", response_model=DeviceReportResponse)
async def create_device_report(
    device_id: int,
    report_data: DeviceReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建设备报表"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    report = DeviceReport(device_id=device_id, **report_data.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.put("/{device_id}/reports/{report_id}", response_model=DeviceReportResponse)
async def update_device_report(
    device_id: int,
    report_id: int,
    report_data: DeviceReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新设备报表"""
    report = db.query(DeviceReport).filter(
        DeviceReport.id == report_id,
        DeviceReport.device_id == device_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    
    for key, value in report_data.model_dump().items():
        setattr(report, key, value)
    
    db.commit()
    db.refresh(report)
    return report


@router.delete("/{device_id}/reports/{report_id}")
async def delete_device_report(
    device_id: int,
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除设备报表"""
    report = db.query(DeviceReport).filter(
        DeviceReport.id == report_id,
        DeviceReport.device_id == device_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    
    db.delete(report)
    db.commit()
    return {"code": 200, "message": "删除成功"}


# ========== 报告管理 ==========
@router.get("/{device_id}/alarms")
async def get_device_alarms(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取设备报告列表"""
    alarms = db.query(DeviceAlarm).filter(DeviceAlarm.device_id == device_id).all()
    return success_response(data=[{
        "id": a.id,
        "device_id": a.device_id,
        "alarm_name": a.alarm_name,
        "resolution": a.resolution,
        "page_type": a.page_type
    } for a in alarms])


@router.post("/{device_id}/alarms", response_model=DeviceAlarmResponse)
async def create_device_alarm(
    device_id: int,
    alarm_data: DeviceAlarmCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建设备报告"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    alarm = DeviceAlarm(device_id=device_id, **alarm_data.model_dump())
    db.add(alarm)
    db.commit()
    db.refresh(alarm)
    return alarm


@router.put("/{device_id}/alarms/{alarm_id}", response_model=DeviceAlarmResponse)
async def update_device_alarm(
    device_id: int,
    alarm_id: int,
    alarm_data: DeviceAlarmUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新设备报告"""
    alarm = db.query(DeviceAlarm).filter(
        DeviceAlarm.id == alarm_id,
        DeviceAlarm.device_id == device_id
    ).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    for key, value in alarm_data.model_dump().items():
        setattr(alarm, key, value)
    
    db.commit()
    db.refresh(alarm)
    return alarm


@router.delete("/{device_id}/alarms/{alarm_id}")
async def delete_device_alarm(
    device_id: int,
    alarm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除设备报告"""
    alarm = db.query(DeviceAlarm).filter(
        DeviceAlarm.id == alarm_id,
        DeviceAlarm.device_id == device_id
    ).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    db.delete(alarm)
    db.commit()
    return {"code": 200, "message": "删除成功"}
