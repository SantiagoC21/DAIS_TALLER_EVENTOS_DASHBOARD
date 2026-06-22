# routers/events.py
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from models.event import EventType
from schemas.event import EventCreate, EventOut, EventListResponse
from services.event_service import create_event, get_events
from services.alarm_service import (
    open_alarm_session,
    close_alarm_session,
    increment_volume_override,
    increment_biometric_fail,
)
from services.notifier import process_pending_notifications

router = APIRouter(prefix="/events", tags=["Events"])

# Tipos de evento que abren una sesión de alarma
ALARM_OPEN_TYPES = {EventType.ALARM_TRIGGERED}

# Tipos de evento que cierran una sesión de alarma y su razón
ALARM_CLOSE_TYPES = {
    EventType.ALARM_STOPPED_AUTO:       "AUTO",
    EventType.ALARM_STOPPED_BIOMETRIC:  "BIOMETRIC",
    EventType.ALARM_STOPPED_MANUAL:     "MANUAL",
}


@router.post("/", response_model=EventOut, status_code=201)
async def report_event(
    data:               EventCreate,
    background_tasks:   BackgroundTasks,
    db:                 Session = Depends(get_db),
):
    """
    La app Android reporta cualquier evento del sistema.
    El servidor:
      1. Persiste el evento
      2. Abre/cierra sesiones de alarma según el tipo
      3. Incrementa contadores de bypass si aplica
      4. Dispara notificación por email en background si severity >= 2
    """
    # 1. Persistir evento
    event = create_event(db, data)

    # 2. Manejo de sesiones de alarma
    if event.event_type in ALARM_OPEN_TYPES and event.mac_address:
        duration_cfg = (data.payload or {}).get("alarm_duration_secs", 30)
        open_alarm_session(db, event, duration_cfg)

    elif event.event_type in ALARM_CLOSE_TYPES and event.mac_address:
        stop_reason = ALARM_CLOSE_TYPES[event.event_type]
        close_alarm_session(db, event.mac_address, event, stop_reason)

    # 3. Contadores de bypass
    elif event.event_type == EventType.VOLUME_OVERRIDE_ATTEMPT and event.mac_address:
        increment_volume_override(db, event.mac_address)

    elif event.event_type == EventType.BIOMETRIC_FAILED and event.mac_address:
        increment_biometric_fail(db, event.mac_address)

    # 4. Notificación en background (no bloquea la respuesta al Android)
    if event.severity >= 2:
        background_tasks.add_task(process_pending_notifications, db)

    return event


@router.get("/", response_model=EventListResponse)
def list_events(
    page:       int             = Query(default=1, ge=1),
    page_size:  int             = Query(default=50, ge=1, le=200),
    severity:   int | None      = Query(default=None, ge=1, le=3),
    event_type: EventType | None = Query(default=None),
    mac:        str | None      = Query(default=None),
    db:         Session         = Depends(get_db),
):
    """
    Lista eventos con filtros opcionales:
    - severity: 1=INFO, 2=WARN, 3=CRIT (filtra >= al valor dado)
    - event_type: filtra por tipo exacto
    - mac: filtra por MAC address
    """
    items, total = get_events(db, page, page_size, severity, event_type, mac)
    return EventListResponse(total=total, page=page, page_size=page_size, items=items)