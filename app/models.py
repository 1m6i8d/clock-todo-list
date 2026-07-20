"""
Database models for Clock.

CATEGORY_COLORS lives here now (moved from pages.py) since Task is
the thing that owns "color" — this stays the single source of truth
for category -> color, same as before.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

CATEGORY_COLORS = {
    "Health": "#2F5A45",
    "Work": "#5B7FB5",
    "Home": "#D98A3D",
    "Personal": "#7B6A9C",
}
DEFAULT_COLOR = "#8A8778"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship("Task", backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="Personal")
    done = db.Column(db.Boolean, default=False)
    start = db.Column(db.Float, nullable=False)  # decimal hour, e.g. 9.5 = 9:30
    end = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(20), nullable=True)  # explicit override, optional

    def display_color(self):
        return self.color or CATEGORY_COLORS.get(self.category, DEFAULT_COLOR)

    def to_dict(self):
        """Matches the shape DUMMY_TASKS used, so dashboard.html and
        clock.js need no changes to how they read a task."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "done": self.done,
            "start": self.start,
            "end": self.end,
            "color": self.display_color(),
        }