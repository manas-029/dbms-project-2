from datetime import datetime, timezone
from .extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class User(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", index=True)
    is_active = db.Column(db.Boolean, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True))

    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    social_accounts = db.relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    platforms = db.relationship("ConnectedPlatform", back_populates="user", cascade="all, delete-orphan")
    consents = db.relationship("Consent", back_populates="user", cascade="all, delete-orphan")
    risks = db.relationship("RiskAssessment", back_populates="user", cascade="all, delete-orphan")
    alerts = db.relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    deletion_requests = db.relationship("DeletionRequest", back_populates="user", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    analytics = db.relationship("Analytics", back_populates="user", cascade="all, delete-orphan")


class Profile(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    phone = db.Column(db.String(30))
    public_username = db.Column(db.String(80))
    location = db.Column(db.String(100))
    privacy_goal = db.Column(db.String(255), default="Reduce public exposure")
    user = db.relationship("User", back_populates="profile")


class SocialAccount(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    profile_url = db.Column(db.String(255))
    visibility = db.Column(db.String(30), default="Public")
    sensitive_data = db.Column(db.String(255), default="Email, location")
    user = db.relationship("User", back_populates="social_accounts")


class ConnectedPlatform(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    data_collected = db.Column(db.String(255), nullable=False)
    permissions = db.Column(db.String(255), nullable=False)
    third_party_access = db.Column(db.Boolean, default=False)
    privacy_setting = db.Column(db.String(30), default="Medium")
    last_activity_date = db.Column(db.Date)
    retention_months = db.Column(db.Integer, default=12)
    breach_found = db.Column(db.Boolean, default=False)
    user = db.relationship("User", back_populates="platforms")


class Consent(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_name = db.Column(db.String(120), nullable=False)
    permission = db.Column(db.String(160), nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(30), default="Granted", index=True)
    granted_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    expires_at = db.Column(db.DateTime(timezone=True))
    shared_with = db.Column(db.String(255), default="Internal analytics")
    user = db.relationship("User", back_populates="consents")


class RiskAssessment(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    level = db.Column(db.String(20), nullable=False, index=True)
    factors = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    user = db.relationship("User", back_populates="risks")


class Alert(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(20), default="Medium", index=True)
    is_read = db.Column(db.Boolean, default=False)
    source = db.Column(db.String(80), default="Risk Engine")
    user = db.relationship("User", back_populates="alerts")


class DeletionRequest(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_name = db.Column(db.String(120), nullable=False)
    data_type = db.Column(db.String(120), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(30), default="Pending", index=True)
    admin_note = db.Column(db.String(255))
    completed_at = db.Column(db.DateTime(timezone=True))
    user = db.relationship("User", back_populates="deletion_requests")


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), index=True)
    action = db.Column(db.String(160), nullable=False, index=True)
    entity = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(60))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    user = db.relationship("User")


class Notification(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = db.Column(db.String(30), default="In-app")
    subject = db.Column(db.String(160), nullable=False)
    body = db.Column(db.String(255), nullable=False)
    is_sent = db.Column(db.Boolean, default=False)
    user = db.relationship("User", back_populates="notifications")


class Analytics(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    month = db.Column(db.String(20), nullable=False)
    exposure_score = db.Column(db.Integer, nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)
    consent_count = db.Column(db.Integer, nullable=False)
    platform_count = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", back_populates="analytics")


class Admin(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    department = db.Column(db.String(120), default="Privacy Operations")
    privileges = db.Column(db.String(255), default="users,risks,audit,deletions")
    user = db.relationship("User")
