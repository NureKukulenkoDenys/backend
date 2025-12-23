from pydantic import BaseModel
from datetime import datetime
from typing import List
from pydantic import BaseModel


class AdministratorItem(BaseModel):
    id: str
    email: str
    name: str | None
    created_at: datetime | None

class AdministratorListResponse(BaseModel):
    administrators: list[AdministratorItem]

class AdministratorDetailResponse(BaseModel):
    id: str
    email: str
    name: str | None
    created_at: datetime | None

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class AdministratorCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)


class AdministratorCreateResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

class EmergencyServiceItem(BaseModel):
    id: int
    name: str
    email: str
    contact_phone: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class EmergencyServiceListResponse(BaseModel):
    emergency_services: list[EmergencyServiceItem]

class EmergencyServiceDetailResponse(BaseModel):
    id: int
    name: str
    email: str
    contact_phone: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class EmergencyServiceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, title="Назва служби")
    email: EmailStr
    password: str = Field(..., min_length=6)
    contact_phone: str | None = Field(
        default=None,
        title="Контактний телефон"
    )

class EmergencyServiceCreateResponse(BaseModel):
    id: int
    name: str
    email: str
    contact_phone: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class AssignBuildingsRequest(BaseModel):
    building_ids: List[int]


class AssignBuildingsResponse(BaseModel):
    emergency_service_id: int
    assigned_buildings: List[int]

class BusinessItem(BaseModel):
    id: int
    email: str
    business_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class BusinessListResponse(BaseModel):
    businesses: List[BusinessItem]

class BusinessDetailResponse(BaseModel):
    id: int
    email: str
    business_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class AdminBuildingItem(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    business_user_id: int
    emergency_service_id: int | None

    class Config:
        from_attributes = True


class AdminBuildingListResponse(BaseModel):
    buildings: list[AdminBuildingItem]

class AdminBuildingDetailResponse(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    business_user_id: int
    emergency_service_id: int | None

    class Config:
        from_attributes = True

class AdminDeviceItem(BaseModel):
    id: int
    building_id: int
    serial_number: str
    model: str
    supports_valve: bool
    active: bool

    class Config:
        from_attributes = True


class AdminDeviceListResponse(BaseModel):
    devices: list[AdminDeviceItem]

class AdminDeviceDetailResponse(BaseModel):
    id: int
    building_id: int
    serial_number: str
    model: str
    supports_valve: bool
    active: bool

    building_address: str
    business_name: str

    class Config:
        from_attributes = True

class AdminIncidentResponse(BaseModel):
    id: int
    severity: str
    status: str
    detected_at: datetime
    description: str | None

    building_id: int
    building_address: str

    business_name: str
    emergency_service_name: str | None

    class Config:
        from_attributes = True

class AdminIncidentDetailResponse(BaseModel):
    id: int
    severity: str
    status: str
    detected_at: datetime
    description: str | None

    building_id: int
    building_name: str
    building_address: str
    latitude: float
    longitude: float

    business_id: int
    business_name: str
    business_email: str

    emergency_service_id: int | None
    emergency_service_name: str | None

    sensor_id: int | None

    class Config:
        from_attributes = True

from pydantic import BaseModel


class AdminIncidentStatisticsResponse(BaseModel):
    total_incidents: int

    open: int
    acknowledged: int
    in_progress: int
    resolved: int

    warning: int
    critical: int


