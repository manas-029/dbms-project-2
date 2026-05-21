from datetime import date
from server.extensions import db
from server.models import RiskAssessment


def calculate_risk(user):
    """Calculate risk with readable rules for DBMS project presentation."""
    score = 0
    factors = []

    public_accounts = [a for a in user.social_accounts if a.visibility.lower() == "public"]
    if public_accounts:
        score += min(25, len(public_accounts) * 8)
        factors.append(f"{len(public_accounts)} public social profile(s)")

    if len(user.platforms) > 4:
        score += 15
        factors.append("Many connected apps/websites")

    weak_settings = [p for p in user.platforms if p.privacy_setting.lower() == "weak"]
    if weak_settings:
        score += min(20, len(weak_settings) * 10)
        factors.append("Weak privacy settings found")

    sensitive = [p for p in user.platforms if any(word in p.data_collected.lower() for word in ["phone", "location", "payment", "health", "address"])]
    if sensitive:
        score += min(20, len(sensitive) * 5)
        factors.append("Sensitive personal data stored")

    breached = [p for p in user.platforms if p.breach_found]
    if breached:
        score += 25
        factors.append("Possible breach exposure")

    over_retained = [p for p in user.platforms if p.retention_months > 24]
    if over_retained:
        score += 10
        factors.append("Over-retention beyond 24 months")

    expired_consents = [c for c in user.consents if c.expires_at and c.expires_at.date() < date.today() and c.status == "Granted"]
    if expired_consents:
        score += 10
        factors.append("Expired consent still granted")

    score = min(score, 100)
    if score < 35:
        level = "Low"
        recommendation = "Keep reviewing consent expiry and avoid unnecessary public profile details."
    elif score < 70:
        level = "Medium"
        recommendation = "Revoke unused permissions, make social profiles private, and shorten retention periods."
    else:
        level = "High"
        recommendation = "Add cleanup tasks for risky platforms and immediately revoke sensitive permissions."

    assessment = RiskAssessment(
        user_id=user.id,
        score=score,
        level=level,
        factors=", ".join(factors) or "No major risk factors detected",
        recommendation=recommendation,
    )
    db.session.add(assessment)
    db.session.commit()
    return assessment
