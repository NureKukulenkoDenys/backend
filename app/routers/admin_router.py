from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import bcrypt

from app.db.database import get_db
from app.db import models
from app.schemas import administrator_schemas
from app.core.security import role_required


router = APIRouter(prefix="/admin", tags=["Administrators"])



@router.get(
    "/emergency-services",
    response_model=administrator_schemas.EmergencyServiceListResponse,
    summary="Get all emergency services",
    description="Отримати список усіх екстрених служб"
)
def get_all_emergency_services(
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    services = db.query(models.EmergencyService).all()

    return administrator_schemas.EmergencyServiceListResponse(
        emergency_services=services
    )


@router.get(
    "/emergency-services/{service_id}",
    response_model=administrator_schemas.EmergencyServiceDetailResponse,
    summary="Get emergency service details",
    description="Отримати деталі конкретної екстреної служби"
)
def get_emergency_service(
    service_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    service = (
        db.query(models.EmergencyService)
        .filter(models.EmergencyService.id == service_id)
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency service not found"
        )

    return service


@router.post(
    "/emergency-services",
    response_model=administrator_schemas.EmergencyServiceCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create emergency service",
    description="Створити нову екстрену службу"
)
def create_emergency_service(
    data: administrator_schemas.EmergencyServiceCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):

    existing_service = (
        db.query(models.EmergencyService)
        .filter(models.EmergencyService.email == data.email)
        .first()
    )

    if existing_service:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Emergency service with this email already exists"
        )

    hashed_password = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


    service = models.EmergencyService(
        name=data.name,
        email=data.email,
        password=hashed_password,
        contact_phone=data.contact_phone
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return service


@router.delete(
    "/emergency-services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete emergency service",
    description="Видалити екстрену службу (доступно лише адміністратору)"
)
def delete_emergency_service(
    service_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    service = (
        db.query(models.EmergencyService)
        .filter(models.EmergencyService.id == service_id)
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency service not found"
        )


    buildings_count = (
        db.query(models.Building)
        .filter(models.Building.emergency_service_id == service_id)
        .count()
    )

    if buildings_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete emergency service with assigned buildings"
        )

    db.delete(service)
    db.commit()


    return

@router.get(
    "/buildings/unassigned",
    response_model=list[administrator_schemas.AdminBuildingResponse],
    summary="Get unassigned buildings",
    description="Отримати всі будівлі, які не закріплені за жодною екстреною службою"
)
def get_unassigned_buildings(
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    buildings = (
        db.query(models.Building)
        .filter(models.Building.emergency_service_id.is_(None))
        .order_by(models.Building.id)
        .all()
    )

    return buildings

@router.post(
    "/emergency-services/{service_id}/assign-buildings",
    response_model=administrator_schemas.AssignBuildingsResponse,
    summary="Assign buildings to emergency service",
    description="Призначити екстренну службу для списку будівель"
)
def assign_buildings_to_emergency_service(
    service_id: int,
    data: administrator_schemas.AssignBuildingsRequest,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):

    service = (
        db.query(models.EmergencyService)
        .filter(models.EmergencyService.id == service_id)
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency service not found"
        )

    if not data.building_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Building IDs list cannot be empty"
        )


    buildings = (
        db.query(models.Building)
        .filter(models.Building.id.in_(data.building_ids))
        .all()
    )

    found_ids = {b.id for b in buildings}
    missing_ids = set(data.building_ids) - found_ids

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Buildings not found: {list(missing_ids)}"
        )


    for building in buildings:
        building.emergency_service_id = service_id

    db.commit()

    return administrator_schemas.AssignBuildingsResponse(
        emergency_service_id=service_id,
        assigned_buildings=data.building_ids
    )


@router.get(
    "/businesses",
    response_model=administrator_schemas.BusinessListResponse,
    summary="Get all businesses",
    description="Отримати список усіх бізнес-користувачів"
)
def get_all_businesses(
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    businesses = db.query(models.BusinessUser).all()

    return administrator_schemas.BusinessListResponse(
        businesses=[
            administrator_schemas.BusinessItem(
                id=b.id,
                email=b.email,
                business_name=b.business_name,
                created_at=b.created_at
            )
            for b in businesses
        ]
    )


@router.get(
    "/businesses/{business_id}",
    response_model=administrator_schemas.BusinessDetailResponse,
    summary="Get business details",
    description="Отримати детальну інформацію про бізнес-користувача"
)
def get_business_by_id(
    business_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    business = (
        db.query(models.BusinessUser)
        .filter(models.BusinessUser.id == business_id)
        .first()
    )

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    return administrator_schemas.BusinessDetailResponse(
        id=business.id,
        email=business.email,
        business_name=business.business_name,
        created_at=business.created_at
    )


@router.delete(
    "/businesses/{business_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete business",
    description="Видалити бізнес-користувача та всі повʼязані з ним дані"
)
def delete_business(
    business_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    business = (
        db.query(models.BusinessUser)
        .filter(models.BusinessUser.id == business_id)
        .first()
    )

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    

    db.delete(business)
    db.commit()


    return


@router.post(
    "/businesses/{business_id}/block",
    status_code=status.HTTP_200_OK,
    summary="Block business",
    description="Заблокувати бізнес-користувача"
)
def block_business(
    business_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    business = (
        db.query(models.BusinessUser)
        .filter(models.BusinessUser.id == business_id)
        .first()
    )

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    if business.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business already blocked"
        )

    business.is_blocked = True
    db.commit()

    return {
        "message": "Business blocked successfully",
        "business_id": business.id,
        "status": "blocked"
    }


@router.get(
    "/buildings",
    response_model=administrator_schemas.AdminBuildingListResponse,
    summary="Get all buildings",
    description="Отримати список усіх будівель у системі"
)
def get_all_buildings(
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    buildings = db.query(models.Building).all()

    return administrator_schemas.AdminBuildingListResponse(
        buildings=buildings
    )


@router.get(
    "/buildings/{building_id}",
    response_model=administrator_schemas.AdminBuildingDetailResponse,
    summary="Get building details",
    description="Отримати детальну інформацію про будівлю"
)
def get_building_by_id(
    building_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    building = (
        db.query(models.Building)
        .filter(models.Building.id == building_id)
        .first()
    )

    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )

    return building


@router.get(
    "/devices",
    response_model=administrator_schemas.AdminDeviceListResponse,
    summary="Get all IoT devices",
    description="Отримати список усіх IoT-пристроїв у системі"
)
def get_all_devices(
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    devices = db.query(models.IoTDevice).all()

    data = [
        administrator_schemas.AdminDeviceItem(
            id=d.id,
            building_id=d.building_id,
            serial_number=d.serial_number,
            model=d.model,
            supports_valve=bool(d.supports_valve),
            active=bool(d.active)
        )
        for d in devices
    ]

    return administrator_schemas.AdminDeviceListResponse(devices=data)


@router.get(
    "/devices/{device_id}",
    response_model=administrator_schemas.AdminDeviceDetailResponse,
    summary="Get IoT device details",
    description="Отримати детальну інформацію про IoT-пристрій"
)
def get_device_detail(
    device_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    device = (
        db.query(models.IoTDevice)
        .join(models.Building, models.IoTDevice.building_id == models.Building.id)
        .join(models.BusinessUser, models.Building.business_user_id == models.BusinessUser.id)
        .filter(models.IoTDevice.id == device_id)
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IoT device not found"
        )

    return administrator_schemas.AdminDeviceDetailResponse(
        id=device.id,
        building_id=device.building_id,
        serial_number=device.serial_number,
        model=device.model,
        supports_valve=bool(device.supports_valve),
        active=bool(device.active),
        building_address=device.building.address,
        business_name=device.building.business_user.business_name
    )

@router.get(
    "/incidents/statistics",
    response_model=administrator_schemas.AdminIncidentStatisticsResponse,
    summary="Incidents statistics",
    description="Статистика по інцидентах у системі"
)
def get_incident_statistics(
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    total = db.query(models.Incident).count()

    open_count = db.query(models.Incident).filter(models.Incident.status == "open").count()
    acknowledged_count = db.query(models.Incident).filter(models.Incident.status == "acknowledged").count()
    in_progress_count = db.query(models.Incident).filter(models.Incident.status == "in_progress").count()
    resolved_count = db.query(models.Incident).filter(models.Incident.status == "resolved").count()

    warning_count = db.query(models.Incident).filter(models.Incident.severity == "warning").count()
    critical_count = db.query(models.Incident).filter(models.Incident.severity == "critical").count()

    return administrator_schemas.AdminIncidentStatisticsResponse(
        total_incidents=total,
        open=open_count,
        acknowledged=acknowledged_count,
        in_progress=in_progress_count,
        resolved=resolved_count,
        warning=warning_count,
        critical=critical_count
    )

@router.get(
    "/incidents",
    response_model=list[administrator_schemas.AdminIncidentResponse],
    summary="Get all incidents",
    description="Отримати всі інциденти в системі"
)
def get_all_incidents(
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    incidents = (
        db.query(models.Incident)
        .join(models.Building, models.Incident.building_id == models.Building.id)
        .join(models.BusinessUser, models.Building.business_user_id == models.BusinessUser.id)
        .outerjoin(
            models.EmergencyService,
            models.Building.emergency_service_id == models.EmergencyService.id
        )
        .order_by(models.Incident.detected_at.desc())
        .all()
    )

    result = []

    for i in incidents:
        result.append(
            administrator_schemas.AdminIncidentResponse(
                id=i.id,
                severity=i.severity,
                status=i.status,
                detected_at=i.detected_at,
                description=i.description,
                building_id=i.building_id,
                building_address=i.building.address,
                business_name=i.building.business_user.business_name,
                emergency_service_name=(
                    i.building.emergency_service.name
                    if i.building.emergency_service
                    else None
                )
            )
        )

    return result


@router.get(
    "/incidents/{incident_id}",
    response_model=administrator_schemas.AdminIncidentDetailResponse,
    summary="Get incident details",
    description="Отримати детальну інформацію про інцидент"
)
def get_incident_detail(
    incident_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    incident = (
        db.query(models.Incident)
        .join(models.Building, models.Incident.building_id == models.Building.id)
        .join(models.BusinessUser, models.Building.business_user_id == models.BusinessUser.id)
        .outerjoin(
            models.EmergencyService,
            models.Building.emergency_service_id == models.EmergencyService.id
        )
        .filter(models.Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    building = incident.building
    business = building.business_user
    emergency = building.emergency_service

    return administrator_schemas.AdminIncidentDetailResponse(
        id=incident.id,
        severity=incident.severity,
        status=incident.status,
        detected_at=incident.detected_at,
        description=incident.description,

        building_id=building.id,
        building_name=building.name,
        building_address=building.address,
        latitude=building.latitude,
        longitude=building.longitude,

        business_id=business.id,
        business_name=business.business_name,
        business_email=business.email,

        emergency_service_id=emergency.id if emergency else None,
        emergency_service_name=emergency.name if emergency else None,

        sensor_id=incident.sensor_id
    )






@router.get(
    "/all",
    response_model=administrator_schemas.AdministratorListResponse
)
def get_all_admins(
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    admins = db.query(models.Administrator).all()

    data = [
        administrator_schemas.AdministratorItem(
            id=str(a.id),
            email=a.email,
            name=a.name,
            created_at=a.created_at
        )
        for a in admins
    ]

    return administrator_schemas.AdministratorListResponse(administrators=data)



@router.post(
    "",
    response_model=administrator_schemas.AdministratorDetailResponse,
    status_code=status.HTTP_201_CREATED
)
def create_administrator(
    data: administrator_schemas.AdministratorCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):

    existing_admin = (
        db.query(models.Administrator)
        .filter(models.Administrator.email == data.email)
        .first()
    )

    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Administrator with this email already exists"
        )

    
    hashed_password = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    new_admin = models.Administrator(
        email=data.email,
        password=hashed_password,
        name=data.name
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return administrator_schemas.AdministratorDetailResponse(
        id=str(new_admin.id),
        email=new_admin.email,
        name=new_admin.name,
        created_at=new_admin.created_at
    )



@router.get(
    "/{admin_id}",
    response_model=administrator_schemas.AdministratorDetailResponse
)
def get_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["administrator"]))
):
    admin = db.query(models.Administrator).filter_by(id=admin_id).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrator not found"
        )

    return administrator_schemas.AdministratorDetailResponse(
        id=str(admin.id),
        email=admin.email,
        name=admin.name,
        created_at=admin.created_at
    )



@router.delete(
    "/{admin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete administrator",
    description="Видалити адміністратора (доступно лише адміністратору)"
)
def delete_administrator(
    admin_id: int,
    db: Session = Depends(get_db),
    user_data=Depends(role_required(["administrator"]))
):
    current_admin: models.Administrator = user_data["user"]

    if current_admin.id == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself"
        )

    admin = (
        db.query(models.Administrator)
        .filter(models.Administrator.id == admin_id)
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrator not found"
        )

    db.delete(admin)
    db.commit()

    return
