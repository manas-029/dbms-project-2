from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from server.extensions import db
from server.middleware.auth import login_required, current_user
from server.models import ConnectedPlatform, Consent, DeletionRequest, Alert, Profile, SocialAccount
from server.services.audit_service import log_action
from server.services.notification_service import generate_privacy_alerts
from server.services.risk_service import calculate_risk

web_bp = Blueprint("web", __name__)


@web_bp.app_context_processor
def inject_user():
    return {"current_user": current_user()}


@web_bp.route("/")
def landing():
    return render_template("landing.html")


@web_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    latest_risk = calculate_risk(user)
    stats = {
        "platforms": len(user.platforms),
        "socials": len(user.social_accounts),
        "consents": len(user.consents),
        "alerts": Alert.query.filter_by(user_id=user.id, is_read=False).count(),
        "sensitive": sum(1 for p in user.platforms if "phone" in p.data_collected.lower() or "location" in p.data_collected.lower()),
        "deletions": len(user.deletion_requests),
        "granted_consents": sum(1 for c in user.consents if c.status == "Granted"),
        "revoked_consents": sum(1 for c in user.consents if c.status == "Revoked"),
        "pending_cleanup": sum(1 for item in user.deletion_requests if item.status in ["Pending", "In Progress"]),
    }
    return render_template("dashboard/index.html", user=user, risk=latest_risk, stats=stats)


@web_bp.route("/platforms", methods=["GET", "POST"])
@login_required
def platforms():
    user = current_user()
    if request.method == "POST":
        platform = ConnectedPlatform(
            user_id=user.id,
            name=request.form["name"],
            category=request.form["category"],
            data_collected=request.form["data_collected"],
            permissions=request.form["permissions"],
            third_party_access=bool(request.form.get("third_party_access")),
            privacy_setting=request.form["privacy_setting"],
            retention_months=int(request.form.get("retention_months", 12)),
            breach_found=bool(request.form.get("breach_found")),
        )
        db.session.add(platform)
        db.session.commit()
        log_action(user.id, "CREATE_PLATFORM", "ConnectedPlatform", platform.name)
        calculate_risk(user)
        flash("Platform added and risk score updated.", "success")
        return redirect(url_for("web.platforms"))
    return render_template("dashboard/platforms.html", platforms=user.platforms, socials=user.social_accounts)


@web_bp.route("/social-accounts", methods=["POST"])
@login_required
def add_social_account():
    user = current_user()
    account = SocialAccount(
        user_id=user.id,
        platform=request.form["platform"],
        username=request.form["username"],
        profile_url=request.form.get("profile_url"),
        visibility=request.form["visibility"],
        sensitive_data=request.form.get("sensitive_data", "Email"),
    )
    db.session.add(account)
    db.session.commit()
    log_action(user.id, "CREATE_SOCIAL_ACCOUNT", "SocialAccount", account.platform)
    calculate_risk(user)
    flash("Social account added.", "success")
    return redirect(url_for("web.platforms"))


@web_bp.route("/social-accounts/<int:account_id>/delete", methods=["POST"])
@login_required
def delete_social_account(account_id):
    user = current_user()
    account = SocialAccount.query.filter_by(id=account_id, user_id=user.id).first_or_404()
    platform = account.platform
    db.session.delete(account)
    db.session.commit()
    log_action(user.id, "DELETE_SOCIAL_ACCOUNT", "SocialAccount", platform)
    calculate_risk(user)
    flash("Social account deleted.", "success")
    return redirect(url_for("web.platforms"))


@web_bp.route("/consents", methods=["GET", "POST"])
@login_required
def consents():
    user = current_user()
    if request.method == "POST":
        consent = Consent(
            user_id=user.id,
            platform_name=request.form["platform_name"],
            permission=request.form["permission"],
            purpose=request.form["purpose"],
            status=request.form["status"],
            shared_with=request.form.get("shared_with", "Internal analytics"),
        )
        db.session.add(consent)
        db.session.commit()
        log_action(user.id, "CREATE_CONSENT", "Consent", consent.platform_name)
        flash("Consent record saved.", "success")
        return redirect(url_for("web.consents"))
    return render_template("dashboard/consents.html", consents=user.consents)


@web_bp.route("/consents/<int:consent_id>/toggle", methods=["POST"])
@login_required
def toggle_consent(consent_id):
    user = current_user()
    consent = Consent.query.filter_by(id=consent_id, user_id=user.id).first_or_404()
    consent.status = "Revoked" if consent.status == "Granted" else "Granted"
    db.session.commit()
    log_action(user.id, "UPDATE_CONSENT", "Consent", f"{consent.platform_name} set to {consent.status}")
    flash("Consent status updated.", "success")
    return redirect(url_for("web.consents"))


@web_bp.route("/consents/<int:consent_id>/delete", methods=["POST"])
@login_required
def delete_consent(consent_id):
    user = current_user()
    consent = Consent.query.filter_by(id=consent_id, user_id=user.id).first_or_404()
    platform = consent.platform_name
    db.session.delete(consent)
    db.session.commit()
    log_action(user.id, "DELETE_CONSENT", "Consent", platform)
    calculate_risk(user)
    flash("Consent record deleted.", "success")
    return redirect(url_for("web.consents"))


@web_bp.route("/risk")
@login_required
def risk_center():
    user = current_user()
    risk = calculate_risk(user)
    factor_help = {
        "public social": "Public profiles can expose your username, photos, location, or personal details to anyone.",
        "connected": "More connected apps means more places where your data may be stored or shared.",
        "weak privacy": "Weak settings usually mean more data is visible or shared by default.",
        "sensitive": "Sensitive data like phone, address, location, payment, or health details increases privacy risk.",
        "breach": "A breach flag means the platform may have exposed user data before.",
        "retention": "Long retention means the platform keeps your data for more time than needed.",
        "expired consent": "Expired consent still marked as granted should be reviewed or revoked.",
    }
    factors = []
    for factor in [item.strip() for item in risk.factors.split(",") if item.strip()]:
        detail = "This item affected the latest risk score."
        lower_factor = factor.lower()
        for keyword, explanation in factor_help.items():
            if keyword in lower_factor:
                detail = explanation
                break
        factors.append({"label": factor, "detail": detail})
    return render_template("dashboard/risk.html", risk=risk, risks=user.risks[-8:], factors=factors)


@web_bp.route("/deletion-requests", methods=["GET", "POST"])
@login_required
def deletion_requests():
    user = current_user()
    if request.method == "POST":
        deletion = DeletionRequest(
            user_id=user.id,
            platform_name=request.form["platform_name"],
            data_type=request.form["data_type"],
            reason=request.form["reason"],
        )
        db.session.add(deletion)
        db.session.commit()
        log_action(user.id, "CREATE_DELETION_REQUEST", "DeletionRequest", deletion.platform_name)
        flash("Cleanup task saved.", "success")
        return redirect(url_for("web.deletion_requests"))
    reminders = [
        {
            "platform": item.platform_name,
            "data": item.data_type,
            "status": item.status,
            "message": f"Reminder: check whether {item.data_type} on {item.platform_name} has been cleaned up. Current status is {item.status}.",
        }
        for item in user.deletion_requests
        if item.status in ["Pending", "In Progress"]
    ]
    return render_template("dashboard/deletions.html", requests=user.deletion_requests, reminders=reminders)


@web_bp.route("/cleanup-tasks/<int:request_id>/delete", methods=["POST"])
@login_required
def delete_cleanup_task(request_id):
    user = current_user()
    cleanup = DeletionRequest.query.filter_by(id=request_id, user_id=user.id).first_or_404()
    platform = cleanup.platform_name
    db.session.delete(cleanup)
    db.session.commit()
    log_action(user.id, "DELETE_CLEANUP_TASK", "DeletionRequest", platform)
    flash("Cleanup task deleted.", "success")
    return redirect(url_for("web.deletion_requests"))


@web_bp.route("/alerts")
@login_required
def alerts():
    user = current_user()
    if request.args.get("generate"):
        created = generate_privacy_alerts(user)
        flash(f"Generated {len(created)} privacy alert(s).", "info")
        return redirect(url_for("web.alerts"))
    return render_template("dashboard/alerts.html", alerts=user.alerts)


@web_bp.route("/alerts/<int:alert_id>/read", methods=["POST"])
@login_required
def mark_alert_read(alert_id):
    user = current_user()
    alert = Alert.query.filter_by(id=alert_id, user_id=user.id).first_or_404()
    alert.is_read = True
    db.session.commit()
    log_action(user.id, "READ_ALERT", "Alert", alert.title)
    return redirect(url_for("web.alerts"))


@web_bp.route("/analytics")
@login_required
def analytics():
    flash("Analytics are now included inside the dashboard.", "info")
    return redirect(url_for("web.dashboard"))


@web_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = current_user()
    if request.method == "POST":
        user.name = request.form["name"]
        user.profile = user.profile or Profile(user_id=user.id)
        user.profile.phone = request.form.get("phone")
        user.profile.public_username = request.form.get("public_username")
        user.profile.location = request.form.get("location")
        user.profile.privacy_goal = request.form.get("privacy_goal")
        db.session.commit()
        log_action(user.id, "UPDATE_PROFILE", "Profile", "Profile settings updated")
        flash("Settings saved.", "success")
        return redirect(url_for("web.settings"))
    return render_template("dashboard/settings.html", user=user)
