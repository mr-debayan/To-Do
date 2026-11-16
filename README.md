# To-Do App (Flask + SQLite)

A small, self-contained to-do app: add, edit, complete, and delete tasks, with
filtering and progress tracking. Tasks are stored in SQLite, so they survive
restarts.

The project is deliberately kept to plain Flask, Jinja templates, and vanilla
CSS/JS — no build step, no API keys — so it is easy to read, extend, and explain
as a course project for the AI Crafting program (ANNAM.AI / Vicharanashala Lab,
IIT Ropar).

## Features

- Add tasks (up to 200 characters, blank input ignored)
- Mark tasks complete / incomplete with one click
- Edit a task title inline
- Delete a task (with confirmation)
- Filter by All / Active / Done, with live counts
- Progress bar with completion percentage
- "Clear completed tasks" shortcut
- Keyboard shortcut: press `N` or `/` to jump to the new-task field
- Responsive layout with automatic light/dark theme

## Requirements

- Python 3.9+
- Flask 3.x (installed below)

## Run it

```bash
cd "Default Project"

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> in your browser.

The database file `todo.db` is created automatically on first run. Delete it to
start with a clean list.

## Project layout

```
app.py                 Flask app: routes, SQLite helpers, template filter
requirements.txt       Runtime dependencies
requirements-dev.txt   Test dependencies (pytest)
todo.db                SQLite database (created on first run)
templates/
  index.html           Single Jinja template for the whole UI
static/
  style.css            Styling, light/dark themes, responsive layout
  app.js               Inline editing, delete confirmation, keyboard shortcut
tests/
  test_app.py          Automated pytest suite (17 tests)
TESTING.md             Manual checklist + how to run the tests
```

## Testing

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
```

The suite covers adding, editing, deleting, completing, filtering, escaping, and
validation, each against a temporary database. See [TESTING.md](TESTING.md) for
the full manual checklist.

## Routes

| Method | Path                   | Purpose                          |
| ------ | ---------------------- | -------------------------------- |
| GET    | `/`                    | Task list (supports `?filter=`)  |
| POST   | `/add`                 | Create a task                    |
| POST   | `/toggle/<id>`         | Toggle done / not done           |
| POST   | `/edit/<id>`           | Update a task title              |
| POST   | `/delete/<id>`         | Delete one task                  |
| POST   | `/clear-completed`     | Delete all completed tasks       |

## How it works

- Each request gets its own SQLite connection, tracked via Flask's `g` object
  and closed in `teardown_appcontext`.
- All state-changing actions are POST requests, and every one redirects back to
  the list while preserving the active filter (Post/Redirect/Get).
- Jinja auto-escaping protects task titles in the page; titles are also trimmed
  and length-limited on the server.

## Notes for taking it further

This is a learning project, not a hardened production service. Before putting it
online you would want to add CSRF protection (e.g. Flask-WTF), authentication if
lists should be private, and run it behind a production server (e.g. Gunicorn)
with `debug=False`.

## Ideas for extending it

- Due dates and a "Today" view
- Task notes or subtasks
- Drag-and-drop reordering
- User accounts and per-user lists
- A JSON API plus a React front end
