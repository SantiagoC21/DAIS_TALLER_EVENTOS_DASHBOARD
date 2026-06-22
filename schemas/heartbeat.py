# schemas/heartbeat.py
from datetime import datetime
from pydantic import BaseModel


class HeartbeatCreate(BaseModel):
    """Lo que la app Android manda en POST /heartbeat"""
    bt_enabled:         bool
    service_active:     bool
    monitored_count:    int     = 0
    android_api:        int | None = None
    app_version:        str | None = None


class HeartbeatOut(BaseModel):
    """Lo que el servidor devuelve sobre el último heartbeat"""
    id:                 int
    bt_enabled:         bool
    service_active:     bool
    monitored_count:    int
    android_api:        int | None
    app_version:        str | None
    received_at:        datetime

    model_config = {"from_attributes": True}


class SystemStatusOut(BaseModel):
    """Estado general del sistema para el dashboard"""
    status:             str         # "ONLINE" | "OFFLINE" | "NO_DATA"
    last_heartbeat:     HeartbeatOut | None
    seconds_since_ping: int | None  # segundos desde el último heartbeat