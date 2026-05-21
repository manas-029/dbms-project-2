from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from server.extensions import db
from server.models import User, Profile
from server.utils.security import hash_password, verify_password, is_valid_email, strong_password, create_token
from server.services.audit_service import log_action

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        if not name or not is_valid_email(email) or not strong_password(password):
            flash("Use a valid email and a password with 8+ chars, upper/lowercase and number.", "danger")
            return render_template("auth/register.html")
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "warning")
            return render_template("auth/register.html")
        user = User(name=name, email=email, password_hash=hash_password(password))
        db.session.add(user)
        db.session.flush()
        db.session.add(Profile(user_id=user.id, public_username=name.lower().replace(" ", "_")))
        db.session.commit()
        log_action(user.id, "REGISTER", "User", "New user registration")
        session["user_id"] = user.id
        flash("Welcome! Your tracker is ready.", "success")
        return redirect(url_for("web.dashboard"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not verify_password(password, user.password_hash):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
        session.permanent = True
        session["user_id"] = user.id
        log_action(user.id, "LOGIN", "User", "Web session login")
        return redirect(url_for("admin.dashboard" if user.role == "admin" else "web.dashboard"))
    return render_template("auth/login.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    demo_token = None
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        user = User.query.filter_by(email=email).first()
        if user:
            demo_token = create_token(user)
            log_action(user.id, "FORGOT_PASSWORD", "User", "Demo reset token generated")
        flash("If the email exists, a reset link has been simulated below.", "info")
    return render_template("auth/forgot.html", demo_token=demo_token)


@auth_bp.route("/logout")
def logout():
    user_id = session.get("user_id")
    session.clear()
    if user_id:
        log_action(user_id, "LOGOUT", "User", "Web session logout")
    flash("You have been logged out.", "info")
    return redirect(url_for("web.landing"))
