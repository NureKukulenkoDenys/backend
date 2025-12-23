from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import role_required
from app.db import models
from app.schemas import emergency_schemas

router = APIRouter(
    prefix="/emergency",
    tags=["Emergency Service"]
)


# ----------------------------------
# GET CURRENT EMERGENCY SERVICE PROFILE
# ----------------------------------
@router.get(
    "/me",
    response_model=emergency_schemas.EmergencyServiceProfileResponse,
    summary="Get emergency service profile",
    description="Отримати профіль поточної екстренної служби"
)
def get_my_profile(
    user_data=Depends(role_required(["emergency_service"])),
    db: Session = Depends(get_db)
):
    emergency_service: models.EmergencyService = user_data["user"]

    return emergency_schemas.EmergencyServiceProfileResponse(
        id=emergency_service.id,
        name=emergency_service.name,
        email=emergency_service.email,
        contact_phone=emergency_service.contact_phone,
        created_at=emergency_service.created_at
    )


# ----------------------------------
# GET INCIDENTS THAT REQUIRE RESPONSE
# ----------------------------------
@router.get(
    "/incidents",
    response_model=list[emergency_schemas.EmergencyIncidentResponse],
    summary="Get incidents that require response",
    description="Отримати інциденти, що потребують реагування екстренної служби"
)
def get_emergency_incidents(
    user_data=Depends(role_required(["emergency_service"])),
    db: Session = Depends(get_db)
):
    emergency_service: models.EmergencyService = user_data["user"]

    incidents = (
        db.query(models.Incident)
        .join(models.Building, models.Incident.building_id == models.Building.id)
        .filter(
            models.Building.emergency_service_id == emergency_service.id,
            models.Incident.status.in_(["open", "acknowledged"])
        )
        .order_by(models.Incident.detected_at.desc())
        .all()
    )

    return incidents

# ----------------------------------
# GET BUILDING DETAILS FOR EMERGENCY SERVICE
# ----------------------------------
@router.get(
    "/buildings/{building_id}",
    response_model=emergency_schemas.EmergencyBuildingDetailResponse,
    summary="Get building details",
    description="Отримати деталі будівлі для швидкого реагування екстренної служби"
)
def get_emergency_building(
    building_id: int,
    user_data=Depends(role_required(["emergency_service"])),
    db: Session = Depends(get_db)
):
    emergency_service: models.EmergencyService = user_data["user"]

    building = (
        db.query(models.Building)
        .filter(
            models.Building.id == building_id,
            models.Building.emergency_service_id == emergency_service.id
        )
        .first()
    )

    if not building:
        raise HTTPException(
            status_code=404,
            detail="Building not found or access denied"
        )

    return building


# ----------------------------------
# ACCEPT INCIDENT
# ----------------------------------
# ----------------------------------
# ACCEPT INCIDENT
# ----------------------------------
@router.post(
    "/incidents/{incident_id}/accept",
    status_code=status.HTTP_200_OK,
    summary="Accept incident",
    description="Взяти інцидент в роботу екстренною службою"
)
def accept_incident(
    incident_id: int,
    user_data=Depends(role_required(["emergency_service"])),
    db: Session = Depends(get_db)
):
    emergency_service: models.EmergencyService = user_data["user"]

    incident = (
        db.query(models.Incident)
        .join(models.Building, models.Incident.building_id == models.Building.id)
        .filter(
            models.Incident.id == incident_id,
            models.Building.emergency_service_id == emergency_service.id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or access denied"
        )

    if incident.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incident cannot be accepted (current status: {incident.status})"
        )

    # ✅ ВАЖЛИВО: встановлюємо обидва поля
    incident.status = "in_progress"
    incident.handled_by_service_id = emergency_service.id

    db.commit()
    db.refresh(incident)

    return {
        "message": "Incident accepted and taken into work",
        "incident_id": incident.id,
        "new_status": incident.status,
        "handled_by_service_id": incident.handled_by_service_id
    }


# ----------------------------------
# RESOLVE INCIDENT
# ----------------------------------
@router.post(
    "/incidents/{incident_id}/resolve",
    status_code=status.HTTP_200_OK,
    summary="Resolve incident",
    description="Завершити інцидент екстренною службою"
)
def resolve_incident(
    incident_id: int,
    user_data=Depends(role_required(["emergency_service"])),
    db: Session = Depends(get_db)
):
    emergency_service: models.EmergencyService = user_data["user"]

    incident = (
        db.query(models.Incident)
        .join(models.Building, models.Incident.building_id == models.Building.id)
        .filter(
            models.Incident.id == incident_id,
            models.Building.emergency_service_id == emergency_service.id
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or access denied"
        )

    # ❗ Завершити можна лише інцидент у роботі
    if incident.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incident cannot be resolved (current status: {incident.status})"
        )

    # ✅ Завершуємо інцидент
    incident.status = "resolved"
    db.commit()

    return {
        "message": "Incident resolved successfully",
        "incident_id": incident.id,
        "new_status": incident.status
    }


# ----------------------------------
# GET ACCEPTED INCIDENTS (IN PROGRESS)
# ----------------------------------
@router.get(
    "/incidents/accepted",
    response_model=list[emergency_schemas.EmergencyIncidentResponse],
    summary="Get accepted incidents",
    description="Отримати інциденти, які екстренна служба вже взяла в роботу"
)
def get_accepted_incidents(
    user_data=Depends(role_required(["emergency_service"])),
    db: Session = Depends(get_db)
):
    emergency_service: models.EmergencyService = user_data["user"]

    incidents = (
        db.query(models.Incident)
        .join(models.Building, models.Incident.building_id == models.Building.id)
        .filter(
            models.Incident.status == "in_progress",
            models.Incident.handled_by_service_id == emergency_service.id
        )
        .order_by(models.Incident.detected_at.desc())
        .all()
    )

    return incidents


# ----------------------------------
# GET RESOLVED INCIDENTS (HISTORY)
# ----------------------------------
@router.get(
    "/incidents/history",
    response_model=list[emergency_schemas.EmergencyIncidentResponse],
    summary="Get resolved incidents",
    description="Отримати завершені інциденти екстренної служби"
)
def get_resolved_incidents(
    user_data=Depends(role_required(["emergency_service"])),
    db: Session = Depends(get_db)
):
    emergency_service: models.EmergencyService = user_data["user"]

    incidents = (
        db.query(models.Incident)
        .filter(
            models.Incident.status == "resolved",
            models.Incident.handled_by_service_id == emergency_service.id
        )
        .order_by(models.Incident.detected_at.desc())
        .all()
    )

    return incidents

# ----------------------------------
# GET INCIDENT LOCATION (MAP)
# ----------------------------------
@router.get(
    "/incidents/{incident_id}/location",
    response_model=emergency_schemas.EmergencyIncidentLocationResponse,
    summary="Get incident location",
    description="Отримати локацію інциденту для відображення на карті"
)
def get_incident_location(
    incident_id: int,
    user_data=Depends(role_required(["emergency_service"])),
    db: Session = Depends(get_db)
):
    emergency_service: models.EmergencyService = user_data["user"]

    result = (
        db.query(
            models.Incident.id.label("incident_id"),
            models.Building.id.label("building_id"),
            models.Building.address,
            models.Building.latitude,
            models.Building.longitude
        )
        .join(models.Building, models.Incident.building_id == models.Building.id)
        .filter(
            models.Incident.id == incident_id,
            models.Building.emergency_service_id == emergency_service.id
        )
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found or access denied"
        )

    return result



