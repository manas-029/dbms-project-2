from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from server.extensions import db
from server.middleware.auth import admin_required
from server.models import User, RiskAssessment, AuditLog, DeletionRequest, Alert
from server.services.audit_service import log_action

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@admin_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    risks = RiskAssessment.query.order_by(RiskAssessment.created_at.desc()).limit(10).all()
    deletions = DeletionRequest.query.order_by(DeletionRequest.created_at.desc()).limit(10).all()
    stats = {
        "users": User.query.count(),
        "high_risks": RiskAssessment.query.filter_by(level="High").count(),
        "pending_deletions": DeletionRequest.query.filter_by(status="Pending").count(),
        "alerts": Alert.query.count(),
    }
    return render_template("admin/dashboard.html", users=users, risks=risks, deletions=deletions, stats=stats)


@admin_bp.route("/users")
@admin_required
def users():
    return render_template("admin/users.html", users=User.query.order_by(User.created_at.desc()).all())


@admin_bp.route("/audit-logs")
@admin_required
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return render_template("admin/audit.html", logs=logs)


@admin_bp.route("/deletion-requests/<int:request_id>/status", methods=["POST"])
@admin_required
def update_deletion_status(request_id):
    deletion = DeletionRequest.query.get_or_404(request_id)
    deletion.status = request.form["status"]
    deletion.admin_note = request.form.get("admin_note")
    if deletion.status == "Completed":
        deletion.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    log_action(deletion.user_id, "ADMIN_UPDATE_DELETION", "DeletionRequest", f"Set to {deletion.status}")
    flash("Cleanup task updated.", "success")
    return redirect(url_for("admin.dashboard"))
