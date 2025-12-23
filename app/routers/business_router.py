from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import role_required
from app.db import models
from app.schemas import business_schemas

router = APIRouter(
    prefix="/business",
    tags=["Business"]
)


# ----------------------------------
# GET CURRENT BUSINESS USER PROFILE
# ----------------------------------
@router.get(
    "/me",
    response_model=business_schemas.BusinessUserResponse
)
def get_my_profile(
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    business_user: models.BusinessUser = user_data["user"]

    return business_schemas.BusinessUserResponse(
        id=business_user.id,
        email=business_user.email,
        business_name=business_user.business_name,
        created_at=business_user.created_at
    )


# ----------------------------------
# GET ALL BUILDINGS OF CURRENT BUSINESS
# ----------------------------------
@router.get(
    "/buildings",
    response_model=list[business_schemas.BusinessBuildingResponse]
)
def get_my_buildings(
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    """
    Отримати всі будівлі поточного власника бізнесу
    """
    business_user: models.BusinessUser = user_data["user"]

    buildings = (
        db.query(models.Building)
        .filter(models.Building.business_user_id == business_user.id)
        .all()
    )

    return [
        business_schemas.BusinessBuildingResponse(
            id=b.id,
            name=b.name,
            address=b.address,
            latitude=b.latitude,
            longitude=b.longitude
        )
        for b in buildings
    ]


# ----------------------------------
# GET IOT DEVICES OF A BUILDING
# ONLY BUSINESS ROLE
# ----------------------------------
@router.get(
    "/buildings/{building_id}/devices",
    response_model=list[business_schemas.BusinessDeviceResponse]
)
def get_building_devices(
    building_id: int,
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    """
    Отримати IoT-пристрої конкретної будівлі.
    Доступ дозволено лише власнику цієї будівлі.
    """
    business_user: models.BusinessUser = user_data["user"]

    # 🔒 Перевірка: будівля належить цьому бізнесу
    building = (
        db.query(models.Building)
        .filter(
            models.Building.id == building_id,
            models.Building.business_user_id == business_user.id
        )
        .first()
    )

    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found or access denied"
        )

    devices = (
        db.query(models.IoTDevice)
        .filter(models.IoTDevice.building_id == building_id)
        .all()
    )

    return [
        business_schemas.BusinessDeviceResponse(
            id=d.id,
            serial_number=d.serial_number,
            model=d.model,
            supports_valve=d.supports_valve,
            active=d.active
        )
        for d in devices
    ]

    # ----------------------------------
# GET ALL INCIDENTS OF CURRENT BUSINESS
# ONLY BUSINESS ROLE
# ----------------------------------
@router.get(
    "/incidents",
    response_model=list[business_schemas.BusinessIncidentResponse]
)
def get_business_incidents(
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    """
    Отримати всі інциденти по обʼєктах поточного бізнесу
    """
    business_user: models.BusinessUser = user_data["user"]

    incidents = (
        db.query(models.Incident)
        .join(models.Building, models.Incident.building_id == models.Building.id)
        .filter(models.Building.business_user_id == business_user.id)
        .order_by(models.Incident.detected_at.desc())
        .all()
    )

    return [
        business_schemas.BusinessIncidentResponse(
            id=i.id,
            building_id=i.building_id,
            sensor_id=i.sensor_id,
            detected_at=i.detected_at,
            severity=i.severity,
            status=i.status,
            description=i.description
        )
        for i in incidents
    ]


# ----------------------------------
# GET ONE INCIDENT DETAILS
# ONLY BUSINESS ROLE
# ----------------------------------
@router.get(
    "/incidents/{incident_id}",
    response_model=business_schemas.BusinessIncidentDetailResponse
)
def get_business_incident(
    incident_id: int,
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    """
    Отримати деталі одного інциденту поточного бізнесу
    """
    business_user: models.BusinessUser = user_data["user"]

    incident = (
        db.query(models.Incident)
        .join(models.Building, models.Incident.building_id == models.Building.id)
        .filter(
            models.Incident.id == incident_id,
            models.Building.business_user_id == business_user.id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or access denied"
        )

    return business_schemas.BusinessIncidentDetailResponse(
        id=incident.id,
        building_id=incident.building_id,
        sensor_id=incident.sensor_id,
        detected_at=incident.detected_at,
        severity=incident.severity,
        status=incident.status,
        description=incident.description
    )



# ----------------------------------
# ACKNOWLEDGE INCIDENT
# ONLY BUSINESS ROLE
# ----------------------------------
@router.post(
    "/incidents/{incident_id}/acknowledge",
    status_code=status.HTTP_200_OK
)
def acknowledge_incident(
    incident_id: int,
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    """
    Підтвердження тривоги власником бізнесу
    """
    business_user: models.BusinessUser = user_data["user"]

    incident = (
        db.query(models.Incident)
        .join(models.Building, models.Incident.building_id == models.Building.id)
        .filter(
            models.Incident.id == incident_id,
            models.Building.business_user_id == business_user.id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or access denied"
        )

    # ❗ Якщо вже підтверджено
    if incident.status == "acknowledged":
        return {
            "message": "Incident already acknowledged"
        }

    # ✅ Підтверджуємо інцидент
    incident.status = "acknowledged"
    db.commit()

    return {
        "message": "Incident acknowledged successfully",
        "incident_id": incident.id,
        "new_status": incident.status
    }

@router.post(
    "/buildings",
    response_model=business_schemas.BusinessBuildingCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Building",
    description="Створити нову будівлю для поточного бізнесу"
)
def create_building(
    building_data: business_schemas.BusinessBuildingCreateRequest,
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    business_user: models.BusinessUser = user_data["user"]

    new_building = models.Building(
        name=building_data.name,
        address=building_data.address,
        latitude=building_data.latitude,
        longitude=building_data.longitude,
        business_user_id=business_user.id
    )

    db.add(new_building)
    db.commit()
    db.refresh(new_building)

    return new_building

# ----------------------------------
# DELETE BUILDING
# ONLY BUSINESS ROLE
# ----------------------------------
@router.delete(
    "/buildings/{building_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Building",
    description="Видалити будівлю, що належить поточному бізнесу"
)
def delete_building(
    building_id: int,
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    business_user: models.BusinessUser = user_data["user"]

    # 🔒 Перевірка: будівля належить бізнесу
    building = (
        db.query(models.Building)
        .filter(
            models.Building.id == building_id,
            models.Building.business_user_id == business_user.id
        )
        .first()
    )

    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found or access denied"
        )

    # 🚨 1. Перевірка НЕ вирішених інцидентів
    active_incidents = (
        db.query(models.Incident)
        .filter(
            models.Incident.building_id == building_id,
            models.Incident.status != "resolved"
        )
        .count()
    )

    if active_incidents > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete building while there are unresolved incidents"
        )

    # 🚨 2. Перевірка IoT-пристроїв
    devices_count = (
        db.query(models.IoTDevice)
        .filter(models.IoTDevice.building_id == building_id)
        .count()
    )

    if devices_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete building while IoT devices are attached"
        )

    # ✅ ВСІ УМОВИ ВИКОНАНІ — МОЖНА ВИДАЛЯТИ
    db.delete(building)
    db.commit()

    return



# ----------------------------------
# CREATE IOT DEVICE FOR BUILDING
# ONLY BUSINESS ROLE
# ----------------------------------
@router.post(
    "/buildings/{building_id}/devices",
    response_model=business_schemas.BusinessDeviceCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add IoT device to building",
    description="Додати IoT-пристрій до будівлі поточного бізнесу"
)
def create_device_for_building(
    building_id: int,
    device_data: business_schemas.BusinessDeviceCreateRequest,
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    business_user: models.BusinessUser = user_data["user"]

    # 🔒 Перевірка: будівля належить цьому бізнесу
    building = (
        db.query(models.Building)
        .filter(
            models.Building.id == building_id,
            models.Building.business_user_id == business_user.id
        )
        .first()
    )

    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found or access denied"
        )

    # 🔁 Перевірка унікальності серійного номера
    existing_device = (
        db.query(models.IoTDevice)
        .filter(models.IoTDevice.serial_number == device_data.serial_number)
        .first()
    )

    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this serial number already exists"
        )

    # ✅ Створення пристрою
    new_device = models.IoTDevice(
        building_id=building_id,
        serial_number=device_data.serial_number,
        model=device_data.model,
        supports_valve=device_data.supports_valve,
        active=True
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return new_device

# ----------------------------------
# DELETE IOT DEVICE
# ONLY BUSINESS ROLE
# ----------------------------------
@router.delete(
    "/devices/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete IoT device",
    description="Видалити IoT-пристрій, що належить поточному бізнесу"
)
def delete_iot_device(
    device_id: int,
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    business_user: models.BusinessUser = user_data["user"]

    # 🔒 Перевірка: пристрій належить будівлі цього бізнесу
    device = (
        db.query(models.IoTDevice)
        .join(models.Building, models.IoTDevice.building_id == models.Building.id)
        .filter(
            models.IoTDevice.id == device_id,
            models.Building.business_user_id == business_user.id
        )
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or access denied"
        )

    db.delete(device)
    db.commit()

    # 204 — успішно, без тіла відповіді
    return

# ----------------------------------
# CREATE SENSOR FOR DEVICE
# ONLY BUSINESS ROLE
# ----------------------------------
@router.post(
    "/devices/{device_id}/sensors",
    response_model=business_schemas.BusinessSensorCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add sensor to IoT device",
    description="Додати сенсор до IoT-пристрою поточного бізнесу"
)
def create_sensor_for_device(
    device_id: int,
    sensor_data: business_schemas.BusinessSensorCreateRequest,
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    business_user: models.BusinessUser = user_data["user"]

    # 🔒 Перевірка: пристрій належить бізнесу
    device = (
        db.query(models.IoTDevice)
        .join(models.Building, models.IoTDevice.building_id == models.Building.id)
        .filter(
            models.IoTDevice.id == device_id,
            models.Building.business_user_id == business_user.id
        )
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or access denied"
        )

    # 🔒 Перевірка порогів
    if sensor_data.threshold_warning >= sensor_data.threshold_critical:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warning threshold must be less than critical threshold"
        )

    new_sensor = models.Sensor(
        device_id=device_id,
        sensor_type=sensor_data.sensor_type,
        unit=sensor_data.unit,
        threshold_warning=sensor_data.threshold_warning,
        threshold_critical=sensor_data.threshold_critical
    )

    db.add(new_sensor)
    db.commit()
    db.refresh(new_sensor)

    return new_sensor






@router.delete(
    "/sensors/{sensor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete sensor",
    description="Видалити сенсор, якщо всі інциденти по ньому врегульовані"
)
def delete_sensor(
    sensor_id: int,
    user_data=Depends(role_required(["business"])),
    db: Session = Depends(get_db)
):
    business_user: models.BusinessUser = user_data["user"]

    # 🔎 Перевірка: сенсор належить бізнесу
    sensor = (
        db.query(models.Sensor)
        .join(models.IoTDevice, models.Sensor.device_id == models.IoTDevice.id)
        .join(models.Building, models.IoTDevice.building_id == models.Building.id)
        .filter(
            models.Sensor.id == sensor_id,
            models.Building.business_user_id == business_user.id
        )
        .first()
    )

    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor not found or access denied"
        )

    # 🚨 Перевірка: чи є НЕ врегульовані інциденти
    active_incidents = (
        db.query(models.Incident)
        .filter(
            models.Incident.sensor_id == sensor_id,
            models.Incident.status != "resolved"
        )
        .count()
    )

    if active_incidents > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete sensor while unresolved incidents exist"
        )

    # ✅ Видалення сенсора (sensor_metrics видаляться каскадно)
    db.delete(sensor)
    db.commit()

    return
