# models/alarm_session.py
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class BTAlarmSession(Base):
    __tablename__ = "bt_alarm_sessions"

    id                      = Column(BigInteger, primary_key=True, autoincrement=True)
    mac_address             = Column(String(17), nullable=False, index=True)
    device_name             = Column(String(100), nullable=False)
    alarm_duration_cfg_secs = Column(Integer, nullable=False)       # duración configurada
    alarm_duration_real_ms  = Column(Integer, nullable=True)        # duración real (ms)
    trigger_event_id        = Column(BigInteger, ForeignKey("bt_events.id", ondelete="SET NULL"), nullable=True)
    stop_event_id           = Column(BigInteger, ForeignKey("bt_events.id", ondelete="SET NULL"), nullable=True)
    stop_reason             = Column(String(30), nullable=True)     # AUTO | BIOMETRIC | MANUAL | None
    volume_override_count   = Column(Integer, nullable=False, default=0)
    biometric_fail_count    = Column(Integer, nullable=False, default=0)
    started_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ended_at                = Column(DateTime(timezone=True), nullable=True)  # None = activa

    # ── Relaciones ──────────────────────────────────────────
    device                  = relationship("BTDevice", back_populates="alarm_sessions",
                                           foreign_keys=[mac_address],
                                           primaryjoin="BTAlarmSession.mac_address == BTDevice.mac_address")
    trigger_event           = relationship("BTEvent", foreign_keys=[trigger_event_id])
    stop_event              = relationship("BTEvent", foreign_keys=[stop_event_id])

    @property
    def is_active(self) -> bool:
        return self.ended_at is None

    def __repr__(self):
        status = "ACTIVE" if self.is_active else f"ENDED({self.stop_reason})"
        return f"<BTAlarmSession id={self.id} mac={self.mac_address} {status}>"