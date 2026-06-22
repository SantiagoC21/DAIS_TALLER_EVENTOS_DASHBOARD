# routers/heartbeat.py
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from config import get_settings
from models.heartbeat import BTMonitorHeartbeat
from schemas.heartbeat import HeartbeatCreate, HeartbeatOut, SystemStatusOut

router   = APIRouter(prefix="/heartbeat", tags=["Heartbeat"])
settings = get_settings()


@router.post("/", response_model=HeartbeatOut, status_code=201)
def receive_heartbeat(data: HeartbeatCreate, db: Session = Depends(get_db)):
    """
    La app Android llama este endpoint periódicamente (cada 60s)
    para indicar que el servicio sigue activo.
    """
    hb = BTMonitorHeartbeat(
        bt_enabled      = data.bt_enabled,
        service_active  = data.service_active,
        monitored_count = data.monitored_count,
        android_api     = data.android_api,
        app_version     = data.app_version,
        received_at     = datetime.now(timezone.utc),
    )
    db.add(hb)
    db.commit()
    db.refresh(hb)
    return hb


@router.get("/latest", response_model=SystemStatusOut)
def get_system_status(db: Session = Depends(get_db)):
    """
    Retorna el estado actual del sistema:
    - ONLINE:   último heartbeat llegó hace menos de HEARTBEAT_TIMEOUT_SECS
    - OFFLINE:  último heartbeat llegó hace más del timeout
    - NO_DATA:  nunca se ha recibido un heartbeat
    """
    last = (
        db.query(BTMonitorHeartbeat)
        .order_by(BTMonitorHeartbeat.received_at.desc())
        .first()
    )

    if last is None:
        return SystemStatusOut(
            status              = "NO_DATA",
            last_heartbeat      = None,
            seconds_since_ping  = None,
        )

    now             = datetime.now(timezone.utc)
    last_received   = last.received_at
    if last_received.tzinfo is None:
        last_received = last_received.replace(tzinfo=timezone.utc)

    seconds_since   = int((now - last_received).total_seconds())
    status          = "ONLINE" if seconds_since <= settings.HEARTBEAT_TIMEOUT_SECS else "OFFLINE"

    return SystemStatusOut(
        status              = status,
        last_heartbeat      = last,
        seconds_since_ping  = seconds_since,
    )