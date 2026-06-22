# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # verifica conexión antes de usarla
    pool_size=5,              # conexiones simultáneas máximas
    max_overflow=10,          # conexiones extra en picos de carga
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


# ── Dependency para inyectar en los routers ─────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()