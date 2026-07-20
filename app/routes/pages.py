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

# ---- Single source of truth for category -> color mapping ----
# Any task without an explicit "color" gets its color resolved here,
# once, before it ever reaches a template or clock.js.
CATEGORY_COLORS = {
    "Health": "#2F5A45",
    "Work": "#5B7FB5",
    "Home": "#D98A3D",
    "Personal": "#7B6A9C",
}
DEFAULT_COLOR = "#8A8778"


def _resolve_color(task):
    """Return task's explicit color if set, else the category default."""
    return task.get("color") or CATEGORY_COLORS.get(task["category"], DEFAULT_COLOR)


# ---- Dummy data (stand-in for the database, until Phase 2) ----
# "color" is omitted unless a task intentionally overrides its
# category's default (see "Standup call" below).
DUMMY_TASKS = [
    {"id": 1, "title": "Morning run", "category": "Health", "done": False, "start": 6.5, "end": 7.5},
    {"id": 2, "title": "Water the plants", "category": "Home", "done": False, "start": 8, "end": 8.5},
    {"id": 3, "title": "Finish Flask routes", "category": "Work", "done": True, "start": 9.5, "end": 12.5},
    {"id": 4, "title": "Standup call", "category": "Work", "done": False, "start": 10, "end": 10.5, "color": "#A4577A"},
    {"id": 5, "title": "Read 20 pages", "category": "Personal", "done": False, "start": 21, "end": 22},
]

# Resolve every task's display color once, here, so both the Jinja
# templates and clock.js (which receives this same data as JSON) read
# from one place instead of keeping their own copies of the mapping.
for _task in DUMMY_TASKS:
    _task["color"] = _resolve_color(_task)


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