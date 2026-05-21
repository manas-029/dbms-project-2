from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify, g
from jwt import InvalidTokenError, ExpiredSignatureError
from server.models import User
from server.utils.security import decode_token


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or user.role != "admin":
            flash("Admin access is required.", "danger")
            return redirect(url_for("web.dashboard"))
        return view(*args, **kwargs)
    return wrapped


def jwt_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "", 1)
        if not token:
            return jsonify({"error": "Missing bearer token"}), 401
        try:
            payload = decode_token(token)
            g.api_user = User.query.get(int(payload["sub"]))
            if not g.api_user:
                return jsonify({"error": "User not found"}), 401
        except ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except (InvalidTokenError, ValueError):
            return jsonify({"error": "Invalid token"}), 401
        return view(*args, **kwargs)
    return wrapped


def api_admin_required(view):
    @wraps(view)
    @jwt_required
    def wrapped(*args, **kwargs):
        if g.api_user.role != "admin":
            return jsonify({"error": "Admin role required"}), 403
        return view(*args, **kwargs)
    return wrapped
