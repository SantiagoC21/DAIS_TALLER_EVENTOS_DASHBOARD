# services/notifier.py
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import get_settings
from models.event import BTEvent
from models.email_log import BTEmailLog
from services.event_service import get_pending_notifications, mark_as_notified

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Severidad legible ────────────────────────────────────────
SEVERITY_LABEL = {1: "INFO", 2: "WARN", 3: "CRIT"}
SEVERITY_COLOR  = {1: "#2196F3", 2: "#FF9800", 3: "#F44336"}


def _build_email_body(event: BTEvent) -> tuple[str, str]:
    """Construye asunto y cuerpo HTML del email."""
    severity_label = SEVERITY_LABEL.get(event.severity, "WARN")
    color          = SEVERITY_COLOR.get(event.severity, "#FF9800")
    device_info    = f"{event.device_name} ({event.mac_address})" if event.mac_address else "Sistema"
    occurred       = event.occurred_at.strftime("%Y-%m-%d %H:%M:%S UTC") if event.occurred_at else "—"

    subject = f"[{severity_label}] Bluetooth Guardian — {event.event_type.value}"

    body = f"""
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="border-left: 5px solid {color}; padding-left: 15px;">
            <h2 style="color: {color};">[{severity_label}] {event.event_type.value}</h2>
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="padding: 6px; font-weight: bold;">Dispositivo</td>
                    <td style="padding: 6px;">{device_info}</td>
                </tr>
                <tr style="background: #f5f5f5;">
                    <td style="padding: 6px; font-weight: bold;">Ocurrió</td>
                    <td style="padding: 6px;">{occurred}</td>
                </tr>
                <tr>
                    <td style="padding: 6px; font-weight: bold;">Tipo de evento</td>
                    <td style="padding: 6px;">{event.event_type.value}</td>
                </tr>
                <tr style="background: #f5f5f5;">
                    <td style="padding: 6px; font-weight: bold;">Payload</td>
                    <td style="padding: 6px;"><code>{event.payload or "—"}</code></td>
                </tr>
            </table>
        </div>
        <p style="color: #999; font-size: 12px; margin-top: 20px;">
            Bluetooth Guardian API — Railway
        </p>
    </body></html>
    """
    return subject, body


async def _send_email(subject: str, body: str) -> None:
    """Envía un email HTML usando aiosmtplib."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.EMAIL_FROM
    msg["To"]      = settings.EMAIL_TO
    msg.attach(MIMEText(body, "html"))

    await aiosmtplib.send(
        msg,
        hostname    = settings.SMTP_HOST,
        port        = settings.SMTP_PORT,
        username    = settings.SMTP_USER,
        password    = settings.SMTP_PASSWORD,
        start_tls   = True,
    )


async def process_pending_notifications(db: Session) -> int:
    """
    Consulta eventos pendientes de notificación y envía emails.
    Registra cada intento en bt_email_log.
    Retorna el número de emails enviados exitosamente.
    """
    pending = get_pending_notifications(db)
    if not pending:
        return 0

    sent_ids    = []
    sent_count  = 0

    for event in pending:
        subject, body = _build_email_body(event)
        log = BTEmailLog(
            event_id    = event.id,
            recipient   = settings.EMAIL_TO,
            subject     = subject,
            status      = "PENDING",
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        try:
            await _send_email(subject, body)
            log.status  = "SENT"
            log.sent_at = datetime.now(timezone.utc)
            sent_ids.append(event.id)
            sent_count += 1
            logger.info(f"Email enviado para evento {event.id} ({event.event_type})")
        except Exception as e:
            log.status      = "FAILED"
            log.error_msg   = str(e)
            logger.error(f"Error enviando email para evento {event.id}: {e}")
        finally:
            db.commit()

    if sent_ids:
        mark_as_notified(db, sent_ids)

    return sent_count