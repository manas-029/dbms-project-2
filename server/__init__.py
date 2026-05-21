from flask import Flask, request
from .config import Config
from .extensions import db, bcrypt


def create_app(config_class=Config):
    """Application factory used by Flask, tests, and Docker."""
    app = Flask(
        __name__,
        template_folder="../client/templates",
        static_folder="../client/static",
    )
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)

    from .routes.auth_routes import auth_bp
    from .routes.web_routes import web_bp
    from .routes.api_routes import api_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return {"error": "Not found"}, 404
        return ("Page not found", 404)

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return ("Something went wrong. Please try again.", 500)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    return app
