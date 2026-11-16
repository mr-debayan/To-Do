"""A simple, persistent to-do app built with Flask and SQLite."""

import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, g, redirect, render_template, request, url_for

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "todo.db")

FILTERS = {"all", "active", "completed"}

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    """Open one connection per request and reuse it within that request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the tasks table if it does not exist yet."""
    with sqlite3.connect(DATABASE) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                done       INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )


init_db()


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

@app.template_filter("short_date")
def short_date(value):
    """Turn SQLite's UTC timestamp into a friendly local date like '16 Nov'."""
    try:
        moment = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        return moment.astimezone().strftime("%d %b")
    except (TypeError, ValueError):
        return value


def current_filter():
    value = request.values.get("filter", "all")
    return value if value in FILTERS else "all"


def back_to_list():
    """Redirect to the list, keeping the active filter."""
    return redirect(url_for("index", filter=current_filter()))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    active_filter = current_filter()

    where = ""
    if active_filter == "active":
        where = "WHERE done = 0"
    elif active_filter == "completed":
        where = "WHERE done = 1"

    db = get_db()
    tasks = db.execute(
        f"SELECT * FROM tasks {where} ORDER BY done ASC, id DESC"
    ).fetchall()

    total = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed = db.execute(
        "SELECT COUNT(*) FROM tasks WHERE done = 1"
    ).fetchone()[0]

    return render_template(
        "index.html",
        tasks=tasks,
        active_filter=active_filter,
        total=total,
        completed=completed,
        remaining=total - completed,
    )


@app.post("/add")
def add_task():
    title = request.form.get("title", "").strip()

    if title:
        db = get_db()
        db.execute("INSERT INTO tasks (title) VALUES (?)", (title[:200],))
        db.commit()

    return back_to_list()


@app.post("/toggle/<int:task_id>")
def toggle_task(task_id):
    db = get_db()
    db.execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))
    db.commit()
    return back_to_list()


@app.post("/edit/<int:task_id>")
def edit_task(task_id):
    title = request.form.get("title", "").strip()

    if title:
        db = get_db()
        db.execute(
            "UPDATE tasks SET title = ? WHERE id = ?", (title[:200], task_id)
        )
        db.commit()

    return back_to_list()


@app.post("/delete/<int:task_id>")
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return back_to_list()


@app.post("/clear-completed")
def clear_completed():
    db = get_db()
    db.execute("DELETE FROM tasks WHERE done = 1")
    db.commit()
    return back_to_list()


if __name__ == "__main__":
    app.run(debug=True)
