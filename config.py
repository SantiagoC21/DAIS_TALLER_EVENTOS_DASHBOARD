# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Base de datos ───────────────────────────────────────
    DATABASE_URL: str

    # ── Email SMTP ──────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str                  # App Password de Gmail
    EMAIL_FROM: str                     # puede ser igual a SMTP_USER
    EMAIL_TO: str                       # destinatario de alertas

    # ── App ─────────────────────────────────────────────────
    APP_TITLE: str = "Bluetooth Guardian API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Heartbeat ───────────────────────────────────────────
    HEARTBEAT_TIMEOUT_SECS: int = 120   # si no llega ping en 2min → OFFLINE

    # ── Notificaciones ──────────────────────────────────────
    MIN_SEVERITY_TO_NOTIFY: int = 2     # 1=INFO, 2=WARN, 3=CRIT

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()