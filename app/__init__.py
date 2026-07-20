"""
Clock - Flask app factory.

Frontend-first setup: templates render with dummy/hardcoded data for now.
Once the DB is ready, routes will pass real data in.
"""
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config.py", silent=True)
    app.config.setdefault("SECRET_KEY", "dev-secret-change-me")

    # Register page routes (frontend-first: these just render templates for now)
    from app.routes.pages import pages_bp
    app.register_blueprint(pages_bp)

    return app
