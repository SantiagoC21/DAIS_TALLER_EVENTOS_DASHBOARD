# schemas/alarm_session.py
from datetime import datetime
from pydantic import BaseModel


class AlarmSessionOut(BaseModel):
    """Lo que el servidor devuelve sobre una sesión de alarma"""
    id:                         int
    mac_address:                str
    device_name:                str
    alarm_duration_cfg_secs:    int
    alarm_duration_real_ms:     int | None
    stop_reason:                str | None
    volume_override_count:      int
    biometric_fail_count:       int
    is_active:                  bool
    started_at:                 datetime
    ended_at:                   datetime | None

    model_config = {"from_attributes": True}


class AlarmSessionListResponse(BaseModel):
    """Respuesta paginada de sesiones"""
    total:      int
    page:       int
    page_size:  int
    items:      list[AlarmSessionOut]