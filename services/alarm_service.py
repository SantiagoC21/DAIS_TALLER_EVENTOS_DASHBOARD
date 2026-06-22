# services/alarm_service.py
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.alarm_session import BTAlarmSession
from models.event import BTEvent, EventType


def open_alarm_session(
    db:             Session,
    event:          BTEvent,
    duration_cfg:   int,
) -> BTAlarmSession:
    """
    Abre una nueva sesión de alarma vinculada al evento que la disparó.
    Cierra cualquier sesión activa previa del mismo dispositivo.
    """
    # Cerrar sesiones activas anteriores del mismo dispositivo (por si acaso)
    _close_stale_sessions(db, event.mac_address)

    session = BTAlarmSession(
        mac_address             = event.mac_address,
        device_name             = event.device_name or "",
        alarm_duration_cfg_secs = duration_cfg,
        trigger_event_id        = event.id,
        started_at              = datetime.now(timezone.utc),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def close_alarm_session(
    db:          Session,
    mac_address: str,
    stop_event:  BTEvent,
    stop_reason: str,           # "AUTO" | "BIOMETRIC" | "MANUAL"
) -> BTAlarmSession | None:
    """
    Cierra la sesión de alarma activa de un dispositivo.
    Calcula la duración real en ms.
    """
    session = _get_active_session(db, mac_address)
    if session is None:
        return None

    now = datetime.now(timezone.utc)
    duration_ms = int((now - session.started_at).total_seconds() * 1000)

    session.ended_at                = now
    session.stop_reason             = stop_reason
    session.stop_event_id           = stop_event.id
    session.alarm_duration_real_ms  = duration_ms
    db.commit()
    db.refresh(session)
    return session


def increment_volume_override(db: Session, mac_address: str) -> None:
    """Incrementa el contador de intentos de bajar volumen en la sesión activa."""
    session = _get_active_session(db, mac_address)
    if session:
        session.volume_override_count += 1
        db.commit()


def increment_biometric_fail(db: Session, mac_address: str) -> None:
    """Incrementa el contador de intentos biométricos fallidos en la sesión activa."""
    session = _get_active_session(db, mac_address)
    if session:
        session.biometric_fail_count += 1
        db.commit()


def get_active_sessions(db: Session) -> list[BTAlarmSession]:
    """Retorna todas las sesiones de alarma actualmente activas."""
    return db.query(BTAlarmSession).filter(BTAlarmSession.ended_at == None).all()


def get_sessions_by_mac(
    db:         Session,
    mac:        str,
    page:       int = 1,
    page_size:  int = 20,
) -> tuple[list[BTAlarmSession], int]:
    query = db.query(BTAlarmSession).filter(BTAlarmSession.mac_address == mac)
    total = query.count()
    items = (
        query
        .order_by(BTAlarmSession.started_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


# ── Helpers privados ────────────────────────────────────────

def _get_active_session(db: Session, mac_address: str) -> BTAlarmSession | None:
    return (
        db.query(BTAlarmSession)
        .filter(
            BTAlarmSession.mac_address == mac_address,
            BTAlarmSession.ended_at == None,
        )
        .first()
    )


def _close_stale_sessions(db: Session, mac_address: str) -> None:
    """Cierra sesiones huérfanas sin fecha de fin (por reinicios inesperados)."""
    stale = (
        db.query(BTAlarmSession)
        .filter(
            BTAlarmSession.mac_address == mac_address,
            BTAlarmSession.ended_at == None,
        )
        .all()
    )
    now = datetime.now(timezone.utc)
    for s in stale:
        s.ended_at      = now
        s.stop_reason   = "AUTO"
    if stale:
        db.commit()