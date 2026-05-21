from datetime import date, timedelta
from server.extensions import db
from server.models import Alert, Notification


def create_alert(user_id, title, message, severity="Medium", source="Risk Engine"):
    alert = Alert(user_id=user_id, title=title, message=message, severity=severity, source=source)
    notification = Notification(
        user_id=user_id,
        subject=title,
        body=f"Email simulation: {message}",
        channel="Email simulation",
        is_sent=True,
    )
    db.session.add_all([alert, notification])
    db.session.commit()
    return alert


def generate_privacy_alerts(user):
    created = []
    for platform in user.platforms:
        if platform.breach_found:
            created.append(create_alert(user.id, "Possible data leak", f"{platform.name} is marked as breach-exposed.", "High", "Breach Monitor"))
        if platform.retention_months > 24:
            created.append(create_alert(user.id, "Retention exceeded", f"{platform.name} stores data for {platform.retention_months} months.", "Medium", "Retention Policy"))

    soon = date.today() + timedelta(days=14)
    for consent in user.consents:
        if consent.expires_at and consent.expires_at.date() <= soon and consent.status == "Granted":
            created.append(create_alert(user.id, "Consent expiring soon", f"{consent.platform_name}: {consent.permission} expires soon.", "Medium", "Consent Monitor"))
    return created
