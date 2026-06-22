# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import engine
from models import BTDevice, BTEvent, BTAlarmSession, BTMonitorHeartbeat, BTEmailLog
from database import Base
from routers import devices_router, events_router, heartbeat_router, dashboard_router

settings = get_settings()


# ── Crear tablas al arrancar (si no existen) ────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# ── Instancia principal ─────────────────────────────────────
app = FastAPI(
    title       = settings.APP_TITLE,
    version     = settings.APP_VERSION,
    description = "API de monitoreo para Bluetooth Guardian — Dashboard Module",
    lifespan    = lifespan,
)


# ── CORS ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins   = ["*"],    # en producción reemplazar por el dominio del dashboard
    allow_methods   = ["*"],
    allow_headers   = ["*"],
)


# ── Routers ─────────────────────────────────────────────────
app.include_router(devices_router)
app.include_router(events_router)
app.include_router(heartbeat_router)
app.include_router(dashboard_router)


# ── Health check ────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "app":      settings.APP_TITLE,
        "version":  settings.APP_VERSION,
        "status":   "ok",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}