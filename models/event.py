# models/event.py
import enum
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database import Base


class EventType(str, enum.Enum):
    # ── Ciclo de vida del servicio ──────────────────────────
    SERVICE_STARTED         = "SERVICE_STARTED"
    SERVICE_STOPPED         = "SERVICE_STOPPED"
    SERVICE_BOOT_RESTART    = "SERVICE_BOOT_RESTART"

    # ── Conexión Bluetooth ──────────────────────────────────
    DEVICE_DISCONNECTED     = "DEVICE_DISCONNECTED"
    DEVICE_RECONNECTED      = "DEVICE_RECONNECTED"
    BT_ADAPTER_OFF          = "BT_ADAPTER_OFF"
    BT_ADAPTER_ON           = "BT_ADAPTER_ON"

    # ── Alarma ──────────────────────────────────────────────
    ALARM_TRIGGERED         = "ALARM_TRIGGERED"
    ALARM_STOPPED_AUTO      = "ALARM_STOPPED_AUTO"
    ALARM_STOPPED_BIOMETRIC = "ALARM_STOPPED_BIOMETRIC"
    ALARM_STOPPED_MANUAL    = "ALARM_STOPPED_MANUAL"

    # ── Volumen ─────────────────────────────────────────────
    VOLUME_OVERRIDE_ATTEMPT = "VOLUME_OVERRIDE_ATTEMPT"

    # ── Autenticación biométrica ────────────────────────────
    BIOMETRIC_SUCCESS       = "BIOMETRIC_SUCCESS"
    BIOMETRIC_FAILED        = "BIOMETRIC_FAILED"
    BIOMETRIC_ERROR         = "BIOMETRIC_ERROR"
    BIOMETRIC_UNAVAILABLE   = "BIOMETRIC_UNAVAILABLE"

    # ── Permisos ────────────────────────────────────────────
    PERMISSION_DENIED       = "PERMISSION_DENIED"


# Severidad por defecto según tipo de evento
EVENT_SEVERITY: dict[EventType, int] = {
    EventType.SERVICE_STARTED:          1,
    EventType.SERVICE_STOPPED:          1,
    EventType.SERVICE_BOOT_RESTART:     1,
    EventType.DEVICE_RECONNECTED:       1,
    EventType.BT_ADAPTER_ON:            1,
    EventType.BIOMETRIC_SUCCESS:        1,

    EventType.DEVICE_DISCONNECTED:      2,
    EventType.ALARM_STOPPED_AUTO:       2,
    EventType.ALARM_STOPPED_BIOMETRIC:  2,
    EventType.ALARM_STOPPED_MANUAL:     2,
    EventType.VOLUME_OVERRIDE_ATTEMPT:  2,
    EventType.BIOMETRIC_FAILED:         2,
    EventType.BIOMETRIC_ERROR:          2,

    EventType.ALARM_TRIGGERED:          3,
    EventType.BT_ADAPTER_OFF:           3,
    EventType.BIOMETRIC_UNAVAILABLE:    3,
    EventType.PERMISSION_DENIED:        3,
}


class BTEvent(Base):
    __tablename__ = "bt_events"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    event_type  = Column(Enum(EventType, name="event_type"), nullable=False, index=True)
    mac_address = Column(String(17), nullable=True, index=True)
    device_name = Column(String(100), nullable=True)
    severity    = Column(Integer, nullable=False, default=2)    # 1=INFO 2=WARN 3=CRIT
    payload     = Column(JSONB, nullable=True)                  # datos extra del evento
    notified    = Column(Boolean, nullable=False, default=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    received_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<BTEvent id={self.id} type={self.event_type} severity={self.severity}>"