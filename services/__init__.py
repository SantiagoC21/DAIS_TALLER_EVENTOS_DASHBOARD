# services/__init__.py
from .device_service import upsert_device, get_all_devices, get_device_by_mac
from .event_service import (
    create_event,
    get_events,
    get_pending_notifications,
    mark_as_notified,
)
from .alarm_service import (
    open_alarm_session,
    close_alarm_session,
    increment_volume_override,
    increment_biometric_fail,
    get_active_sessions,
    get_sessions_by_mac,
)
from .notifier import process_pending_notifications

__all__ = [
    # device
    "upsert_device",
    "get_all_devices",
    "get_device_by_mac",
    # event
    "create_event",
    "get_events",
    "get_pending_notifications",
    "mark_as_notified",
    # alarm
    "open_alarm_session",
    "close_alarm_session",
    "increment_volume_override",
    "increment_biometric_fail",
    "get_active_sessions",
    "get_sessions_by_mac",
    # notifier
    "process_pending_notifications",
]