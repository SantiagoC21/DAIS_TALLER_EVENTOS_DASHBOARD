# models/email_log.py
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class BTEmailLog(Base):
    __tablename__ = "bt_email_log"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id    = Column(BigInteger, ForeignKey("bt_events.id", ondelete="SET NULL"), nullable=True)
    recipient   = Column(String(200), nullable=False)
    subject     = Column(String(300), nullable=False)
    status      = Column(String(10), nullable=False, default="PENDING")  # PENDING | SENT | FAILED
    error_msg   = Column(Text, nullable=True)
    sent_at     = Column(DateTime(timezone=True), nullable=True)
    created_at  = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # ── Relaciones ──────────────────────────────────────────
    event       = relationship("BTEvent", foreign_keys=[event_id])

    def __repr__(self):
        return (
            f"<BTEmailLog id={self.id}"
            f" event={self.event_id}"
            f" status={self.status}"
            f" recipient={self.recipient}>"
        )