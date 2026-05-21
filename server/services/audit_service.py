from flask import request
from server.extensions import db
from server.models import AuditLog


def log_action(user_id, action, entity, details=""):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        details=details,
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
    )
    db.session.add(log)
    db.session.commit()
    return log
