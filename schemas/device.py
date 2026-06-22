# schemas/device.py
from datetime import datetime
from pydantic import BaseModel, field_validator
import re


class DeviceSync(BaseModel):
    """Lo que la app Android manda en POST /devices/sync"""
    mac_address:            str
    device_name:            str
    is_monitored:           bool
    alarm_duration_secs:    int
    registered_at:          int     # epoch ms

    @field_validator("mac_address")
    @classmethod
    def validate_mac(cls, v: str) -> str:
        pattern = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
        if not re.match(pattern, v):
            raise ValueError(f"MAC address inválida: {v}")
        return v.upper()

    @field_validator("alarm_duration_secs")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if not (5 <= v <= 300):
            raise ValueError("alarm_duration_secs debe estar entre 5 y 300")
        return v


class DeviceOut(BaseModel):
    """Lo que el servidor devuelve sobre un dispositivo"""
    id:                     int
    mac_address:            str
    device_name:            str
    is_monitored:           bool
    alarm_duration_secs:    int
    registered_at:          int
    last_seen_at:           datetime | None = None
    created_at:             datetime
    updated_at:             datetime

    model_config = {"from_attributes": True}


class DeviceSyncResponse(BaseModel):
    """Respuesta tras sincronizar un dispositivo"""
    action:     str         # "created" | "updated"
    device:     DeviceOut