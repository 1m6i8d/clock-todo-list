"""
Page routes for Clock - a fullstack Flask to-do list app.

FRONTEND-FIRST NOTE:
Every route below renders a template with hardcoded/dummy data.
Once the DB models are wired up (Phase 2), replace DUMMY_TASKS with
real queries. Templates already expect this exact data shape, so
swapping it later should be a drop-in change, not a rewrite.
"""
from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)

# ---- Dummy data (stand-in for the database, until Phase 2) ----

DUMMY_TASKS = [
    {"id": 1, "title": "Morning run", "category": "Health", "done": False, "start": 6.5, "end": 7.5, "color": "#2F5A45"},
    {"id": 2, "title": "Water the plants", "category": "Home", "done": False, "start": 8, "end": 8.5, "color": "#D98A3D"},
    {"id": 3, "title": "Finish Flask routes", "category": "Work", "done": True, "start": 9.5, "end": 12.5, "color": "#5B7FB5"},
    {"id": 4, "title": "Standup call", "category": "Work", "done": False, "start": 10, "end": 10.5, "color": "#A4577A"},
    {"id": 5, "title": "Read 20 pages", "category": "Personal", "done": False, "start": 21, "end": 22, "color": "#7B6A9C"},
]


@pages_bp.route("/")
def dashboard():
    return render_template("dashboard.html", tasks=DUMMY_TASKS)


@pages_bp.route("/tasks")
def tasks():
    return render_template("tasks.html", tasks=DUMMY_TASKS)


@pages_bp.route("/tasks/new")
def new_task():
    return render_template("new_task.html")


@pages_bp.route("/login")
def login():
    return render_template("login.html")


@pages_bp.route("/signup")
def signup():
    return render_template("signup.html")
