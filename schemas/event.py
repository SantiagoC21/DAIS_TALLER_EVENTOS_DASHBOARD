# schemas/event.py
from datetime import datetime
from pydantic import BaseModel
from models.event import EventType


class EventCreate(BaseModel):
    """Lo que la app Android manda en POST /events"""
    event_type:     EventType
    mac_address:    str | None  = None
    device_name:    str | None  = None
    payload:        dict | None = None
    occurred_at:    str | None  = None  # ISO 8601 — si no viene, el servidor usa NOW()


class EventOut(BaseModel):
    """Lo que el servidor devuelve sobre un evento"""
    id:             int
    event_type:     EventType
    mac_address:    str | None
    device_name:    str | None
    severity:       int
    payload:        dict | None
    notified:       bool
    occurred_at:    datetime
    received_at:    datetime

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    """Respuesta paginada de eventos"""
    total:      int
    page:       int
    page_size:  int
    items:      list[EventOut]