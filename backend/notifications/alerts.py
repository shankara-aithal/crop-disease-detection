"""
Notification / Alert Module
CropGuard AI — BCA AIML Final Year Project

Sends email alerts when a serious crop disease is detected.
Also provides in-app alert logging.

Usage:
    from notifications.alerts import send_disease_alert, log_alert
"""

from flask import current_app
from flask_mail import Message
from database.db_models import db, Alert
from datetime import datetime


# ── Email Alert ───────────────────────────────────────────────────────────────

def send_disease_alert(user_email: str,
                       user_name: str,
                       disease_name: str,
                       crop_type: str,
                       confidence: float,
                       recommendation: str,
                       prediction_id: int) -> bool:
    """
    Send an email alert to the user when a high-confidence disease is detected.

    Returns True if email sent successfully, False otherwise.
    Silently skips if MAIL_USERNAME is not configured.
    """
    if not current_app.config.get('MAIL_USERNAME'):
        current_app.logger.info("[ALERT] Mail not configured — skipping email alert.")
        return False

    if confidence < current_app.config.get('ALERT_CONFIDENCE_THRESHOLD', 0.80):
        return False   # Only alert for high-confidence detections

    try:
        from app import mail
        conf_pct = round(confidence * 100, 1)

        subject = f"🚨 CropGuard Alert: {disease_name} detected in your {crop_type}"

        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
          <div style="background:#16a34a;padding:24px;border-radius:12px 12px 0 0;">
            <h1 style="color:white;margin:0;font-size:22px;">🌿 CropGuard AI Alert</h1>
          </div>
          <div style="background:#fff;padding:24px;border:1px solid #e5e7eb;border-top:none;border-radius:0 0 12px 12px;">
            <p style="color:#374151;">Dear <strong>{user_name}</strong>,</p>
            <p style="color:#374151;">Our AI model has detected a crop disease in your recent scan:</p>

            <div style="background:#fee2e2;border-left:4px solid #ef4444;border-radius:8px;padding:16px;margin:16px 0;">
              <p style="margin:0;color:#991b1b;font-size:18px;font-weight:bold;">{disease_name}</p>
              <p style="margin:6px 0 0;color:#7f1d1d;">Crop: {crop_type} &nbsp;|&nbsp; Confidence: {conf_pct}%</p>
            </div>

            <h3 style="color:#374151;">Recommended Action</h3>
            <p style="color:#374151;line-height:1.6;">{recommendation}</p>

            <p style="color:#374151;">
              <a href="http://localhost:3000/result/{prediction_id}"
                 style="background:#16a34a;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;display:inline-block;">
                View Full Report →
              </a>
            </p>

            <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;">
            <p style="color:#9ca3af;font-size:12px;">
              CropGuard AI · BCA AIML Final Year Project<br>
              This alert was sent because a disease was detected with {conf_pct}% confidence.
            </p>
          </div>
        </div>
        """

        text_body = (
            f"CropGuard AI Disease Alert\n\n"
            f"Disease: {disease_name}\n"
            f"Crop: {crop_type}\n"
            f"Confidence: {conf_pct}%\n\n"
            f"Recommendation: {recommendation}\n\n"
            f"View report: http://localhost:3000/result/{prediction_id}"
        )

        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body,
            body=text_body
        )
        mail.send(msg)
        current_app.logger.info(f"[ALERT] Email sent to {user_email} for {disease_name}")
        return True

    except Exception as e:
        current_app.logger.error(f"[ALERT] Email failed: {e}")
        return False


# ── In-App Alert Logging ──────────────────────────────────────────────────────

def log_alert(user_id: int,
              disease_name: str,
              crop_type: str,
              confidence: float,
              prediction_id: int) -> None:
    """
    Save an alert record to the database so it appears in the
    user's notification bell in the React frontend.
    """
    try:
        alert = Alert(
            user_id=user_id,
            disease_name=disease_name,
            crop_type=crop_type,
            confidence=confidence,
            prediction_id=prediction_id,
            message=f"⚠️ {disease_name} detected in your {crop_type} scan "
                    f"with {round(confidence*100,1)}% confidence.",
            is_read=False
        )
        db.session.add(alert)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"[ALERT] DB log failed: {e}")


def mark_alerts_read(user_id: int) -> None:
    """Mark all unread alerts as read for a user."""
    Alert.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()


def get_unread_count(user_id: int) -> int:
    """Return count of unread alerts for a user."""
    return Alert.query.filter_by(user_id=user_id, is_read=False).count()
