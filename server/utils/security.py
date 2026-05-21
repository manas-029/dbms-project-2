import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app
from email_validator import validate_email, EmailNotValidError
from server.extensions import bcrypt


def hash_password(password):
    return bcrypt.generate_password_hash(password).decode("utf-8")


def verify_password(password, password_hash):
    return bcrypt.check_password_hash(password_hash, password)


def create_token(user):
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=8),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])


def is_valid_email(email):
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def strong_password(password):
    """Simple beginner-friendly password strength check."""
    return (
        len(password) >= 8
        and any(ch.isupper() for ch in password)
        and any(ch.islower() for ch in password)
        and any(ch.isdigit() for ch in password)
    )
