# models/heartbeat.py
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func
from database import Base


class BTMonitorHeartbeat(Base):
    __tablename__ = "bt_monitor_heartbeat"

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    bt_enabled      = Column(Boolean, nullable=False)           # ¿Bluetooth encendido?
    service_active  = Column(Boolean, nullable=False)           # ¿BluetoothMonitorService corriendo?
    monitored_count = Column(Integer, nullable=False, default=0)# dispositivos actualmente monitoreados
    android_api     = Column(Integer, nullable=True)            # versión API del dispositivo
    app_version     = Column(String(20), nullable=True)         # versión de la app
    received_at     = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return (
            f"<BTMonitorHeartbeat id={self.id}"
            f" bt={self.bt_enabled}"
            f" service={self.service_active}"
            f" devices={self.monitored_count}"
            f" received={self.received_at}>"
        )