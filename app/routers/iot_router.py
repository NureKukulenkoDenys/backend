from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.schemas.iot_schemas import (
    SensorDataCreateRequest,
    SensorDataResponse
)

router = APIRouter(
    prefix="/iot",
    tags=["IoT"]
)

@router.post(
    "/sensors/{sensor_id}/data",
    response_model=SensorDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send sensor data"
)
def receive_sensor_data(
    sensor_id: int,
    data: SensorDataCreateRequest,
    db: Session = Depends(get_db)
):
    
    sensor = db.query(models.Sensor).filter(
        models.Sensor.id == sensor_id
    ).first()
    if not sensor:
        raise HTTPException(404, "Sensor not found")

   
    device = db.query(models.IoTDevice).filter(
        models.IoTDevice.id == sensor.device_id
    ).first()

    
    building = db.query(models.Building).filter(
        models.Building.id == device.building_id
    ).first()

    value = data.value
    severity = "normal"
    incident_created = False

    
    if value >= sensor.threshold_critical:
        severity = "critical"
    elif value >= sensor.threshold_warning:
        severity = "warning"

    
    if severity in ("warning", "critical"):
        incident = models.Incident(
            building_id=building.id,
            sensor_id=sensor.id,
            severity=severity,
            status="open",
            description=f"{sensor.sensor_type.upper()} = {value} {sensor.unit}"
        )
        db.add(incident)
        db.commit()
        incident_created = True

    return SensorDataResponse(
        sensor_id=sensor.id,
        value=value,
        severity=severity,
        incident_created=incident_created
    )
