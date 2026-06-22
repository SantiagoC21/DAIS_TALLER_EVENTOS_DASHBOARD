# services/event_service.py
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.event import BTEvent, EventType, EVENT_SEVERITY
from schemas.event import EventCreate


def create_event(db: Session, data: EventCreate) -> BTEvent:
    """
    Inserta un nuevo evento. Asigna severidad automáticamente
    si no viene en el payload según EVENT_SEVERITY.
    """
    occurred_at = datetime.now(timezone.utc)
    if data.occurred_at:
        try:
            occurred_at = datetime.fromisoformat(data.occurred_at)
        except ValueError:
            pass  # si el formato es inválido usa NOW()

    severity = EVENT_SEVERITY.get(data.event_type, 2)

    event = BTEvent(
        event_type  = data.event_type,
        mac_address = data.mac_address,
        device_name = data.device_name,
        severity    = severity,
        payload     = data.payload,
        notified    = False,
        occurred_at = occurred_at,
        received_at = datetime.now(timezone.utc),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_events(
    db:         Session,
    page:       int = 1,
    page_size:  int = 50,
    severity:   int | None = None,
    event_type: EventType | None = None,
    mac:        str | None = None,
) -> tuple[list[BTEvent], int]:
    """
    Retorna eventos paginados con filtros opcionales.
    """
    query = db.query(BTEvent)

    if severity is not None:
        query = query.filter(BTEvent.severity >= severity)
    if event_type is not None:
        query = query.filter(BTEvent.event_type == event_type)
    if mac is not None:
        query = query.filter(BTEvent.mac_address == mac)

    total = query.count()
    items = (
        query
        .order_by(BTEvent.occurred_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_pending_notifications(db: Session) -> list[BTEvent]:
    """
    Eventos WARN y CRIT que aún no fueron notificados por email.
    """
    return (
        db.query(BTEvent)
        .filter(BTEvent.notified == False, BTEvent.severity >= 2)
        .order_by(BTEvent.severity.desc(), BTEvent.occurred_at.asc())
        .all()
    )


def mark_as_notified(db: Session, event_ids: list[int]) -> int:
    """
    Marca una lista de eventos como notificados.
    Retorna el número de filas actualizadas.
    """
    updated = (
        db.query(BTEvent)
        .filter(BTEvent.id.in_(event_ids))
        .update({"notified": True}, synchronize_session=False)
    )
    db.commit()
    return updated