"""
Clock config. Kept minimal for now.
"""
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
SQLALCHEMY_DATABASE_URI = "sqlite:///instance/clock.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
