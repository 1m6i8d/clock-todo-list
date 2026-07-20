"""
Page + CRUD routes for Clock.
Phase 2: DUMMY_TASKS is gone. Everything reads/writes through
SQLAlchemy, scoped to the logged-in user via Flask-Login's current_user.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User, Task

pages_bp = Blueprint("pages", __name__)


# ---- time helpers: <input type="time"> gives "HH:MM", DB stores decimal hours ----

def time_str_to_decimal(time_str):
    hh, mm = time_str.split(":")
    return int(hh) + int(mm) / 60


def decimal_to_time_str(decimal_hours):
    hh = int(decimal_hours)
    mm = round((decimal_hours % 1) * 60)
    return f"{hh:02d}:{mm:02d}"


# ---- dashboard / tasks ----

@pages_bp.route("/")
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.start).all()
    tasks_json = [t.to_dict() for t in tasks]
    return render_template("dashboard.html", tasks=tasks, tasks_json=tasks_json)


@pages_bp.route("/tasks")
@login_required
def tasks():
    task_list = Task.query.filter_by(user_id=current_user.id).order_by(Task.start).all()
    return render_template("tasks.html", tasks=task_list)


@pages_bp.route("/tasks/new", methods=["GET", "POST"])
@login_required
def new_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "Personal")
        start_raw = request.form.get("start", "")
        end_raw = request.form.get("end", "")

        if not title or not start_raw or not end_raw:
            flash("Title, start time, and end time are required.", "error")
            return render_template("new_task.html")

        start = time_str_to_decimal(start_raw)
        end = time_str_to_decimal(end_raw)

        if end <= start:
            flash("End time must be after start time.", "error")
            return render_template("new_task.html")

        task = Task(
            user_id=current_user.id,
            title=title,
            category=category,
            start=start,
            end=end,
        )
        db.session.add(task)
        db.session.commit()
        flash("Task created.", "success")
        return redirect(url_for("pages.dashboard"))

    return render_template("new_task.html")


@pages_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", task.category)
        start_raw = request.form.get("start", "")
        end_raw = request.form.get("end", "")

        if not title or not start_raw or not end_raw:
            flash("Title, start time, and end time are required.", "error")
            return render_template(
                "edit_task.html", task=task,
                start_str=start_raw or decimal_to_time_str(task.start),
                end_str=end_raw or decimal_to_time_str(task.end),
            )

        start = time_str_to_decimal(start_raw)
        end = time_str_to_decimal(end_raw)

        if end <= start:
            flash("End time must be after start time.", "error")
            return render_template(
                "edit_task.html", task=task, start_str=start_raw, end_str=end_raw
            )

        task.title = title
        task.category = category
        task.start = start
        task.end = end
        db.session.commit()
        flash("Task updated.", "success")
        return redirect(url_for("pages.dashboard"))

    return render_template(
        "edit_task.html",
        task=task,
        start_str=decimal_to_time_str(task.start),
        end_str=decimal_to_time_str(task.end),
    )


@pages_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "success")
    return redirect(url_for("pages.dashboard"))


@pages_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.done = not task.done
    db.session.commit()
    return redirect(request.referrer or url_for("pages.dashboard"))


# ---- auth ----

@pages_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("pages.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.name}.", "success")
            return redirect(url_for("pages.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@pages_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("pages.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("signup.html")

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return render_template("signup.html")

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created — welcome!", "success")
        return redirect(url_for("pages.dashboard"))

    return render_template("signup.html")


@pages_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("pages.login"))