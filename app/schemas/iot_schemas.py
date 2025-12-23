# app/schemas/iot_schemas.py
from pydantic import BaseModel

class SensorDataCreateRequest(BaseModel):
    value: float


class SensorDataResponse(BaseModel):
    sensor_id: int
    value: float
    severity: str
    incident_created: bool
