# models/device.py
from sqlalchemy import BigInteger, Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class BTDevice(Base):
    __tablename__ = "bt_devices"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    mac_address         = Column(String(17), nullable=False, unique=True, index=True)
    device_name         = Column(String(100), nullable=False)
    is_monitored        = Column(Boolean, nullable=False, default=True)
    alarm_duration_secs = Column(Integer, nullable=False, default=30)
    registered_at       = Column(BigInteger, nullable=False)        # epoch ms del Android
    last_seen_at        = Column(DateTime(timezone=True), nullable=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ── Relaciones ──────────────────────────────────────────
    alarm_sessions      = relationship("BTAlarmSession", back_populates="device",
                                       foreign_keys="BTAlarmSession.mac_address",
                                       primaryjoin="BTDevice.mac_address == BTAlarmSession.mac_address")

    def __repr__(self):
        return f"<BTDevice mac={self.mac_address} name={self.device_name} monitored={self.is_monitored}>"