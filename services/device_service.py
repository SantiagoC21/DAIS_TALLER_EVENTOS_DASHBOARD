# services/device_service.py
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.device import BTDevice
from schemas.device import DeviceSync


def upsert_device(db: Session, data: DeviceSync) -> tuple[BTDevice, str]:
    """
    Inserta o actualiza un dispositivo según su MAC address.
    Retorna (dispositivo, acción) donde acción es 'created' o 'updated'.
    """
    device = db.query(BTDevice).filter(BTDevice.mac_address == data.mac_address).first()

    if device is None:
        device = BTDevice(
            mac_address         = data.mac_address,
            device_name         = data.device_name,
            is_monitored        = data.is_monitored,
            alarm_duration_secs = data.alarm_duration_secs,
            registered_at       = data.registered_at,
            last_seen_at        = datetime.now(timezone.utc),
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return device, "created"

    # Actualizar campos si ya existe
    device.device_name          = data.device_name
    device.is_monitored         = data.is_monitored
    device.alarm_duration_secs  = data.alarm_duration_secs
    device.last_seen_at         = datetime.now(timezone.utc)
    db.commit()
    db.refresh(device)
    return device, "updated"


def get_all_devices(db: Session) -> list[BTDevice]:
    return db.query(BTDevice).order_by(BTDevice.device_name).all()


def get_device_by_mac(db: Session, mac_address: str) -> BTDevice | None:
    return db.query(BTDevice).filter(BTDevice.mac_address == mac_address).first()