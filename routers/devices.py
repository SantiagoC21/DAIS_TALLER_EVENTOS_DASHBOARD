# routers/devices.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.device import DeviceSync, DeviceOut, DeviceSyncResponse
from services.device_service import upsert_device, get_all_devices, get_device_by_mac

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/sync", response_model=DeviceSyncResponse, status_code=200)
def sync_device(data: DeviceSync, db: Session = Depends(get_db)):
    """
    La app Android llama este endpoint cada vez que:
    - Registra un dispositivo nuevo
    - Activa / desactiva monitoreo
    - Cambia la duración de alarma
    - Elimina un dispositivo (is_monitored=False + flag especial)
    """
    device, action = upsert_device(db, data)
    return DeviceSyncResponse(action=action, device=device)


@router.get("/", response_model=list[DeviceOut])
def list_devices(db: Session = Depends(get_db)):
    """Retorna todos los dispositivos registrados."""
    return get_all_devices(db)


@router.get("/{mac_address}", response_model=DeviceOut)
def get_device(mac_address: str, db: Session = Depends(get_db)):
    """Retorna un dispositivo por su MAC address."""
    device = get_device_by_mac(db, mac_address.upper())
    if not device:
        raise HTTPException(status_code=404, detail=f"Dispositivo {mac_address} no encontrado")
    return device