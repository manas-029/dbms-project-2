from flask import Blueprint, request, jsonify, g
from server.extensions import db
from server.models import User, ConnectedPlatform, Consent, Alert, DeletionRequest, AuditLog, Analytics
from server.utils.security import verify_password, create_token
from server.middleware.auth import jwt_required, api_admin_required
from server.services.risk_service import calculate_risk
from server.services.audit_service import log_action

api_bp = Blueprint("api", __name__)


def platform_json(platform):
    return {
        "id": platform.id,
        "name": platform.name,
        "category": platform.category,
        "dataCollected": platform.data_collected,
        "permissions": platform.permissions,
        "thirdPartyAccess": platform.third_party_access,
        "retentionMonths": platform.retention_months,
        "breachFound": platform.breach_found,
    }


@api_bp.route("/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True)
    user = User.query.filter_by(email=data.get("email", "").lower()).first()
    if not user or not verify_password(data.get("password", ""), user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_token(user)
    log_action(user.id, "API_LOGIN", "User", "JWT issued")
    return jsonify({"token": token, "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}})


@api_bp.route("/me")
@jwt_required
def me():
    user = g.api_user
    return jsonify({"id": user.id, "name": user.name, "email": user.email, "role": user.role})


@api_bp.route("/platforms", methods=["GET", "POST"])
@jwt_required
def platforms():
    user = g.api_user
    if request.method == "POST":
        data = request.get_json(force=True)
        required = ["name", "category", "dataCollected", "permissions"]
        if any(not data.get(key) for key in required):
            return jsonify({"error": "name, category, dataCollected, and permissions are required"}), 400
        platform = ConnectedPlatform(
            user_id=user.id,
            name=data["name"],
            category=data["category"],
            data_collected=data["dataCollected"],
            permissions=data["permissions"],
            third_party_access=bool(data.get("thirdPartyAccess", False)),
            retention_months=int(data.get("retentionMonths", 12)),
            privacy_setting=data.get("privacySetting", "Medium"),
            breach_found=bool(data.get("breachFound", False)),
        )
        db.session.add(platform)
        db.session.commit()
        calculate_risk(user)
        log_action(user.id, "API_CREATE_PLATFORM", "ConnectedPlatform", platform.name)
        return jsonify(platform_json(platform)), 201
    return jsonify([platform_json(p) for p in user.platforms])


@api_bp.route("/consents")
@jwt_required
def consents():
    return jsonify([
        {"id": c.id, "platform": c.platform_name, "permission": c.permission, "purpose": c.purpose, "status": c.status, "sharedWith": c.shared_with}
        for c in g.api_user.consents
    ])


@api_bp.route("/risks")
@jwt_required
def risks():
    risk = calculate_risk(g.api_user)
    return jsonify({"score": risk.score, "level": risk.level, "factors": risk.factors, "recommendation": risk.recommendation})


@api_bp.route("/alerts")
@jwt_required
def alerts():
    return jsonify([{"id": a.id, "title": a.title, "message": a.message, "severity": a.severity, "isRead": a.is_read} for a in g.api_user.alerts])


@api_bp.route("/analytics")
@jwt_required
def analytics():
    return jsonify([
        {"month": a.month, "exposureScore": a.exposure_score, "riskScore": a.risk_score, "consentCount": a.consent_count, "platformCount": a.platform_count}
        for a in g.api_user.analytics
    ])


@api_bp.route("/deletion-requests", methods=["GET", "POST"])
@jwt_required
def deletion_requests():
    user = g.api_user
    if request.method == "POST":
        data = request.get_json(force=True)
        deletion = DeletionRequest(
            user_id=user.id,
            platform_name=data.get("platformName"),
            data_type=data.get("dataType"),
            reason=data.get("reason"),
        )
        if not deletion.platform_name or not deletion.data_type or not deletion.reason:
            return jsonify({"error": "platformName, dataType and reason are required"}), 400
        db.session.add(deletion)
        db.session.commit()
        log_action(user.id, "API_CREATE_DELETION_REQUEST", "DeletionRequest", deletion.platform_name)
        return jsonify({"id": deletion.id, "status": deletion.status}), 201
    return jsonify([{"id": d.id, "platformName": d.platform_name, "dataType": d.data_type, "reason": d.reason, "status": d.status} for d in user.deletion_requests])


@api_bp.route("/admin/audit-logs")
@api_admin_required
def admin_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return jsonify([{"id": l.id, "userId": l.user_id, "action": l.action, "entity": l.entity, "ipAddress": l.ip_address, "createdAt": l.created_at.isoformat()} for l in logs])
