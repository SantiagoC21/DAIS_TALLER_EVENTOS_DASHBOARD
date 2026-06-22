# routers/dashboard.py
from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db
from schemas.dashboard import DashboardSummaryOut, DeviceSummaryOut, PendingNotificationOut
from schemas.heartbeat import SystemStatusOut
from routers.heartbeat import get_system_status
from models.alarm_session import BTAlarmSession
from models.device import BTDevice
from models.event import BTEvent

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

STATIC_DIR = Path(__file__).parent.parent / "static"
cre

@router.get("/ui", include_in_schema=False)
def serve_dashboard():
    """Sirve el dashboard HTML visual."""
    return FileResponse(STATIC_DIR / "dashboard.html")


@router.get("/summary", response_model=DashboardSummaryOut)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Endpoint principal del dashboard. Retorna en una sola llamada:
    - Estado del sistema (ONLINE/OFFLINE/NO_DATA)
    - Resumen por dispositivo (desde vw_device_summary)
    - Últimos 20 eventos
    - Contadores globales
    """
    # Estado del sistema
    system_status: SystemStatusOut = get_system_status(db)

    # Resumen por dispositivo desde la vista SQL
    rows = db.execute(text("SELECT * FROM vw_device_summary ORDER BY device_name")).mappings().all()
    devices = [
        DeviceSummaryOut(
            mac_address             = r["mac_address"],
            device_name             = r["device_name"],
            is_monitored            = r["is_monitored"],
            alarm_duration_secs     = r["alarm_duration_secs"],
            last_seen_at            = r["last_seen_at"],
            total_alarms            = r["total_alarms"] or 0,
            alarm_active            = bool(r["alarm_active"]),
            last_alarm_at           = r["last_alarm_at"],
            total_volume_overrides  = r["total_volume_overrides"] or 0,
            total_biometric_fails   = r["total_biometric_fails"] or 0,
            avg_alarm_duration_secs = float(r["avg_alarm_duration_secs"]) if r["avg_alarm_duration_secs"] else None,
        )
        for r in rows
    ]

    # Últimos 20 eventos
    recent_events = (
        db.query(BTEvent)
        .order_by(BTEvent.occurred_at.desc())
        .limit(20)
        .all()
    )
    recent_events_out = [
        {
            "id":           e.id,
            "event_type":   e.event_type.value,
            "mac_address":  e.mac_address,
            "device_name":  e.device_name,
            "severity":     e.severity,
            "occurred_at":  e.occurred_at.isoformat() if e.occurred_at else None,
        }
        for e in recent_events
    ]

    # Contadores globales
    total_devices       = db.query(BTDevice).count()
    monitored_devices   = db.query(BTDevice).filter(BTDevice.is_monitored == True).count()
    active_alarms_count = db.query(BTAlarmSession).filter(BTAlarmSession.ended_at == None).count()

    return DashboardSummaryOut(
        system_status       = system_status,
        devices             = devices,
        recent_events       = recent_events_out,
        active_alarms_count = active_alarms_count,
        total_devices       = total_devices,
        monitored_devices   = monitored_devices,
    )


@router.get("/events/pending", response_model=list[PendingNotificationOut])
def get_pending_events(db: Session = Depends(get_db)):
    """
    Eventos WARN y CRIT pendientes de notificación.
    Útil para depuración desde el dashboard.
    """
    rows = db.execute(text("SELECT * FROM vw_pending_notifications")).mappings().all()
    return [
        PendingNotificationOut(
            id          = r["id"],
            event_type  = r["event_type"],
            mac_address = r["mac_address"],
            device_name = r["device_name"],
            severity    = r["severity"],
            payload     = r["payload"],
            occurred_at = r["occurred_at"],
        )
        for r in rows
    ]