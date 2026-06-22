# routers/__init__.py
from .devices   import router as devices_router
from .events    import router as events_router
from .heartbeat import router as heartbeat_router
from .dashboard import router as dashboard_router

__all__ = [
    "devices_router",
    "events_router",
    "heartbeat_router",
    "dashboard_router",
]