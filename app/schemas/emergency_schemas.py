from pydantic import BaseModel
from datetime import datetime


class EmergencyServiceProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    contact_phone: str | None
    created_at: datetime

    class Config:
        orm_mode = True

class EmergencyIncidentResponse(BaseModel):
    id: int
    building_id: int
    sensor_id: int | None
    detected_at: datetime
    severity: str
    status: str
    description: str | None

    class Config:
        from_attributes = True

class EmergencyBuildingDetailResponse(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

class EmergencyIncidentLocationResponse(BaseModel):
    incident_id: int
    building_id: int
    address: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
