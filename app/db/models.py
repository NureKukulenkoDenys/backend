from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    func,
    Boolean
)
from sqlalchemy.orm import relationship
from app.db.database import Base


# ---------------------------
# Administrators
# ---------------------------
class Administrator(Base):
    __tablename__ = "administrators"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    emergency_services = relationship("EmergencyService", back_populates="admin")


# ---------------------------
# Emergency Services
# ---------------------------
class EmergencyService(Base):
    __tablename__ = "emergency_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_phone = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    admin_id = Column(Integer, ForeignKey("administrators.id", ondelete="CASCADE"))
    admin = relationship("Administrator", back_populates="emergency_services")


# ---------------------------
class BusinessUser(Base):
    __tablename__ = "business_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    business_name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    is_blocked = Column(Boolean, default=False, nullable=False)


# ---------------------------
# Buildings
# ---------------------------
class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    business_user_id = Column(
        Integer,
        ForeignKey("business_users.id", ondelete="CASCADE"),
        nullable=False
    )

    emergency_service_id = Column(
        Integer,
        ForeignKey("emergency_services.id"),
        nullable=True
    )

    devices = relationship(
        "IoTDevice",
        back_populates="building",
        cascade="all, delete-orphan"
    )

    # ✅ корисн
    business_user = relationship("BusinessUser")
    emergency_service = relationship("EmergencyService")



class IoTDevice(Base):
    __tablename__ = "iot_devices"

    id = Column(Integer, primary_key=True, index=True)

    building_id = Column(
        Integer,
        ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False
    )

    serial_number = Column(String, unique=True, nullable=False)
    model = Column(String, nullable=False)

    supports_valve = Column(Boolean, nullable=False)
    active = Column(Boolean, nullable=False)

    # ✅ ДОДАТИ ОЦЕ
    building = relationship("Building")

    sensors = relationship(
        "Sensor",
        back_populates="device",
        cascade="all, delete-orphan"
    )


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    building_id = Column(
        Integer,
        ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False
    )

    sensor_id = Column(Integer, nullable=True)

    detected_at = Column(DateTime, server_default=func.now(), nullable=False)

    severity = Column(String, nullable=False)
    status = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # ✅ ОЦЕ КРИТИЧНО ДОДАТИ
    handled_by_service_id = Column(
        Integer,
        ForeignKey("emergency_services.id"),
        nullable=True
    )

    admin_id = Column(
        Integer,
        ForeignKey("administrators.id"),
        nullable=True
    )

    building = relationship("Building")
    handled_by_service = relationship("EmergencyService")



# ---------------------------
# Valves
# ---------------------------
class Valve(Base):
    __tablename__ = "valves"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(
        Integer,
        ForeignKey("iot_devices.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    valve_number = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)  # ✅ BOOLEAN
    last_closed_at = Column(DateTime, nullable=True)


# ---------------------------
# Sensors
# ---------------------------
class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(
        Integer,
        ForeignKey("iot_devices.id", ondelete="CASCADE"),
        nullable=False
    )

    sensor_type = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    threshold_warning = Column(Integer, nullable=False)
    threshold_critical = Column(Integer, nullable=False)

    # 🔁 звʼязок назад
    device = relationship("IoTDevice", back_populates="sensors")

    # ✅ каскад на метрики
    metrics = relationship(
        "SensorMetric",
        back_populates="sensor",
        cascade="all, delete-orphan"
    )

class SensorMetric(Base):
    __tablename__ = "sensor_metrics"

    id = Column(Integer, primary_key=True, index=True)

    sensor_id = Column(
        Integer,
        ForeignKey("sensors.id", ondelete="CASCADE"),
        nullable=False
    )

    value = Column(Float, nullable=False)
    recorded_at = Column(DateTime, server_default=func.now())

    sensor = relationship("Sensor", back_populates="metrics")

