from pydantic import BaseModel, Field, constr, confloat
from datetime import datetime


# =========================
# BUSINESS USER
# =========================
class BusinessUserResponse(BaseModel):
    id: int
    email: str
    business_name: str
    created_at: datetime

    class Config:
        orm_mode = True


# =========================
# BUILDINGS
# =========================
class BusinessBuildingResponse(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True


class BusinessBuildingCreateRequest(BaseModel):
    name: constr(min_length=1) = Field(
        ...,
        title="Назва будівлі",
        description="Назва обʼєкта бізнесу (наприклад: Warehouse A)"
    )
    address: constr(min_length=1) = Field(
        ...,
        title="Адреса",
        description="Фізична адреса будівлі"
    )
    latitude: confloat(ge=-90, le=90) = Field(
        ...,
        title="Широта",
        description="Географічна широта (-90 .. 90)"
    )
    longitude: confloat(ge=-180, le=180) = Field(
        ...,
        title="Довгота",
        description="Географічна довгота (-180 .. 180)"
    )


class BusinessBuildingCreateResponse(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    business_user_id: int

    class Config:
        orm_mode = True


# =========================
# IOT DEVICES
# =========================
class BusinessDeviceResponse(BaseModel):
    id: int
    serial_number: str
    model: str
    supports_valve: bool
    active: bool

    class Config:
        orm_mode = True


class BusinessDeviceCreateRequest(BaseModel):
    serial_number: constr(min_length=1) = Field(
        ...,
        title="Серійний номер",
        description="Унікальний серійний номер пристрою (наприклад DEV003)"
    )
    model: constr(min_length=1) = Field(
        ...,
        title="Модель пристрою",
        description="Модель IoT-пристрою"
    )
    supports_valve: bool = Field(
        ...,
        title="Підтримка клапана",
        description="Чи підтримує пристрій керування клапаном"
    )


class BusinessDeviceCreateResponse(BaseModel):
    id: int
    building_id: int
    serial_number: str
    model: str
    supports_valve: bool
    active: bool

    class Config:
        orm_mode = True


# =========================
# SENSORS
# =========================
class BusinessSensorCreateRequest(BaseModel):
    sensor_type: constr(min_length=1) = Field(
        ...,
        title="Тип сенсора",
        description="Тип сенсора (gas, co, smoke)"
    )
    unit: constr(min_length=1) = Field(
        ...,
        title="Одиниця виміру",
        description="Одиниця виміру (ppm, %, mg/m3)"
    )
    threshold_warning: int = Field(
        ...,
        gt=0,
        title="Поріг попередження",
        description="Значення для попереджувального рівня"
    )
    threshold_critical: int = Field(
        ...,
        gt=0,
        title="Критичний поріг",
        description="Значення для аварійного рівня"
    )


class BusinessSensorCreateResponse(BaseModel):
    id: int
    device_id: int
    sensor_type: str
    unit: str
    threshold_warning: int
    threshold_critical: int

    class Config:
        orm_mode = True


# =========================
# INCIDENTS
# =========================
class BusinessIncidentResponse(BaseModel):
    id: int
    building_id: int
    sensor_id: int | None
    detected_at: datetime
    severity: str
    status: str
    description: str | None

    class Config:
        orm_mode = True


class BusinessIncidentDetailResponse(BusinessIncidentResponse):
    pass


class BusinessIncidentAcknowledgeResponse(BaseModel):
    message: str
    incident_id: int
    new_status: str


# =========================
# VALVES
# =========================
class BusinessValveResponse(BaseModel):
    device_id: int
    valve_number: int
    active: bool
    last_closed_at: datetime | None

    class Config:
        orm_mode = True


class BusinessValveCreateRequest(BaseModel):
    valve_number: int = Field(
        ...,
        gt=0,
        title="Номер клапану",
        description="Фізичний номер клапану на пристрої"
    )


class BusinessValveCreateResponse(BaseModel):
    id: int
    device_id: int
    valve_number: int
    active: bool
    last_closed_at: datetime | None

    class Config:
        orm_mode = True


from pydantic import BaseModel


class EmergencyIncidentLocationResponse(BaseModel):
    incident_id: int
    building_id: int
    address: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
