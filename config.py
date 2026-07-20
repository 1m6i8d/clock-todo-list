"""
Clock config. Kept minimal for now.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)  # ensures the folder exists before SQLite needs it

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'clock.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False