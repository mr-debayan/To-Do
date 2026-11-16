"""Automated tests for the to-do app, using Flask's test client."""

import sqlite3

import pytest

import app as todo


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Point the app at a throwaway database for each test."""
    path = tmp_path / "test.db"
    monkeypatch.setattr(todo, "DATABASE", str(path))
    todo.init_db()
    return str(path)


@pytest.fixture
def client(db_path):
    todo.app.config.update(TESTING=True)
    with todo.app.test_client() as test_client:
        yield test_client


def add(client, title, filter_name="all"):
    return client.post(
        "/add",
        data={"title": title, "filter": filter_name},
        follow_redirects=True,
    )


def query(db_path, sql, params=()):
    with sqlite3.connect(db_path) as con:
        return con.execute(sql, params).fetchall()


# ---------------------------------------------------------------------------
# Reading the list
# ---------------------------------------------------------------------------

def test_empty_list_shows_empty_state(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Your list is empty" in response.data


def test_page_is_only_reachable_with_supported_methods(client):
    assert client.get("/add").status_code == 405


# ---------------------------------------------------------------------------
# Adding tasks
# ---------------------------------------------------------------------------

def test_add_task(client, db_path):
    response = add(client, "Buy milk")
    assert response.status_code == 200
    assert b"Buy milk" in response.data
    assert query(db_path, "SELECT title FROM tasks") == [("Buy milk",)]


def test_add_ignores_blank_title(client, db_path):
    add(client, "   ")
    assert query(db_path, "SELECT COUNT(*) FROM tasks") == [(0,)]


def test_add_trims_whitespace(client, db_path):
    add(client, "  Walk the dog  ")
    assert query(db_path, "SELECT title FROM tasks") == [("Walk the dog",)]


def test_add_truncates_long_titles(client, db_path):
    add(client, "x" * 250)
    stored = query(db_path, "SELECT title FROM tasks")[0][0]
    assert len(stored) == 200


def test_title_is_html_escaped(client):
    add(client, "<script>alert(1)</script>")
    response = client.get("/")
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data


# ---------------------------------------------------------------------------
# Completing tasks
# ---------------------------------------------------------------------------

def test_toggle_marks_done_and_back(client, db_path):
    add(client, "Read a chapter")
    task_id = query(db_path, "SELECT id FROM tasks")[0][0]

    client.post(f"/toggle/{task_id}", data={"filter": "all"})
    assert query(db_path, "SELECT done FROM tasks") == [(1,)]

    client.post(f"/toggle/{task_id}", data={"filter": "all"})
    assert query(db_path, "SELECT done FROM tasks") == [(0,)]


def test_toggle_unknown_task_does_not_crash(client):
    response = client.post(
        "/toggle/9999", data={"filter": "all"}, follow_redirects=True
    )
    assert response.status_code == 200


def test_progress_and_counts_update(client):
    add(client, "One")
    add(client, "Two")
    client.post("/toggle/1", data={"filter": "all"})

    response = client.get("/")
    assert b"1 of 2 completed" in response.data
    assert b"50%" in response.data


# ---------------------------------------------------------------------------
# Editing tasks
# ---------------------------------------------------------------------------

def test_edit_changes_title(client, db_path):
    add(client, "Draft report")
    client.post("/edit/1", data={"title": "Finalise report", "filter": "all"})
    assert query(db_path, "SELECT title FROM tasks") == [("Finalise report",)]


def test_edit_ignores_blank_title(client, db_path):
    add(client, "Keep me")
    client.post("/edit/1", data={"title": "   ", "filter": "all"})
    assert query(db_path, "SELECT title FROM tasks") == [("Keep me",)]


# ---------------------------------------------------------------------------
# Deleting tasks
# ---------------------------------------------------------------------------

def test_delete_removes_task(client, db_path):
    add(client, "Temporary")
    client.post("/delete/1", data={"filter": "all"})
    assert query(db_path, "SELECT COUNT(*) FROM tasks") == [(0,)]


def test_clear_completed_keeps_active_tasks(client, db_path):
    add(client, "Done one")
    add(client, "Still active")
    client.post("/toggle/1", data={"filter": "all"})

    client.post("/clear-completed", data={"filter": "all"})
    assert query(db_path, "SELECT title FROM tasks") == [("Still active",)]


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

def test_filters_show_the_right_tasks(client):
    add(client, "Active task")
    add(client, "Finished task")
    client.post("/toggle/2", data={"filter": "all"})

    active = client.get("/?filter=active")
    assert b"Active task" in active.data
    assert b"Finished task" not in active.data

    done = client.get("/?filter=completed")
    assert b"Finished task" in done.data
    assert b"Active task" not in done.data


def test_unknown_filter_falls_back_to_all(client):
    add(client, "Visible task")
    response = client.get("/?filter=banana")
    assert b"Visible task" in response.data


def test_filter_is_preserved_after_actions(client):
    add(client, "Something", filter_name="active")
    response = client.post(
        "/toggle/1", data={"filter": "active"}, follow_redirects=False
    )
    assert response.headers["Location"].endswith("/?filter=active")
