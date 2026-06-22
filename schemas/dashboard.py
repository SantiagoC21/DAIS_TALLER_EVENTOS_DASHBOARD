# schemas/dashboard.py
from datetime import datetime
from pydantic import BaseModel
from schemas.heartbeat import SystemStatusOut


class DeviceSummaryOut(BaseModel):
    """Resumen por dispositivo — mapea vw_device_summary"""
    mac_address:                str
    device_name:                str
    is_monitored:               bool
    alarm_duration_secs:        int
    last_seen_at:               datetime | None
    total_alarms:               int
    alarm_active:               bool
    last_alarm_at:              datetime | None
    total_volume_overrides:     int
    total_biometric_fails:      int
    avg_alarm_duration_secs:    float | None

    model_config = {"from_attributes": True}


class PendingNotificationOut(BaseModel):
    """Evento pendiente de notificación — mapea vw_pending_notifications"""
    id:             int
    event_type:     str
    mac_address:    str | None
    device_name:    str | None
    severity:       int
    payload:        dict | None
    occurred_at:    datetime

    model_config = {"from_attributes": True}


class DashboardSummaryOut(BaseModel):
    """Respuesta completa del endpoint GET /dashboard/summary"""
    system_status:          SystemStatusOut
    devices:                list[DeviceSummaryOut]
    recent_events:          list[dict]
    active_alarms_count:    int
    total_devices:          int
    monitored_devices:      int