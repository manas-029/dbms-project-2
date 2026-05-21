from datetime import datetime, timedelta, timezone
from server import create_app
from server.extensions import db
from server.models import User, Profile, SocialAccount, ConnectedPlatform, Consent, DeletionRequest, Analytics, Admin
from server.utils.security import hash_password
from server.services.risk_service import calculate_risk
from server.services.notification_service import generate_privacy_alerts


def seed_database():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(name="Admin Reviewer", email="admin@privacy.local", password_hash=hash_password("Admin@12345"), role="admin")
        user = User(name="Spoorthi", email="spoorthi123@gmail.com", password_hash=hash_password("Password1"), role="user")
        db.session.add_all([admin, user])
        db.session.flush()
        db.session.add(Admin(user_id=admin.id))
        db.session.add(Profile(user_id=user.id, phone="+91 98765 43210", public_username="aarav.codes", location="Bengaluru", privacy_goal="Reduce old app exposure"))

        socials = [
            SocialAccount(user_id=user.id, platform="Instagram", username="aarav.codes", profile_url="https://instagram.com/aarav.codes", visibility="Public", sensitive_data="Location, photos"),
            SocialAccount(user_id=user.id, platform="LinkedIn", username="aarav-sharma", profile_url="https://linkedin.com/in/aarav-sharma", visibility="Public", sensitive_data="Work history, email"),
        ]
        platforms = [
            ConnectedPlatform(user_id=user.id, name="ShopEase", category="E-commerce", data_collected="Email, phone, address, payment hints", permissions="Email marketing, order history", third_party_access=True, privacy_setting="Weak", retention_months=36, breach_found=True),
            ConnectedPlatform(user_id=user.id, name="FitPulse", category="Health", data_collected="Email, health activity, location", permissions="Location, wearable data", third_party_access=True, privacy_setting="Medium", retention_months=24),
            ConnectedPlatform(user_id=user.id, name="CloudBox", category="Storage", data_collected="Email, files metadata", permissions="Contacts, file access", third_party_access=False, privacy_setting="Strong", retention_months=12),
            ConnectedPlatform(user_id=user.id, name="Streamly", category="Entertainment", data_collected="Email, viewing history", permissions="Recommendations, ad personalization", third_party_access=True, privacy_setting="Medium", retention_months=18),
        ]
        consents = [
            Consent(user_id=user.id, platform_name="ShopEase", permission="Ad personalization", purpose="Targeted offers", status="Granted", expires_at=datetime.now(timezone.utc) + timedelta(days=10), shared_with="Ad partners"),
            Consent(user_id=user.id, platform_name="FitPulse", permission="Location tracking", purpose="Route maps", status="Granted", expires_at=datetime.now(timezone.utc) + timedelta(days=90), shared_with="Map provider"),
            Consent(user_id=user.id, platform_name="Streamly", permission="Viewing analytics", purpose="Recommendations", status="Revoked", expires_at=datetime.now(timezone.utc) - timedelta(days=30), shared_with="Internal analytics"),
        ]
        deletions = [
            DeletionRequest(user_id=user.id, platform_name="OldForum", data_type="Public username and posts", reason="No longer use this account", status="In Progress"),
            DeletionRequest(user_id=user.id, platform_name="ShopEase", data_type="Saved address", reason="Retention is too long", status="Pending"),
        ]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        analytics = [
            Analytics(user_id=user.id, month=m, exposure_score=72 - i * 4, risk_score=80 - i * 5, consent_count=6 - i // 2, platform_count=4 + (i % 2))
            for i, m in enumerate(months)
        ]
        db.session.add_all(socials + platforms + consents + deletions + analytics)
        db.session.commit()
        calculate_risk(user)
        generate_privacy_alerts(user)
        print("Seed complete")


if __name__ == "__main__":
    seed_database()
