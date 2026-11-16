# Testing the To-Do App

Two ways to check the app works: a 5-minute manual pass in the browser, and an
automated pytest suite that covers the same behaviour.

## 1. Automated tests

```bash
git clone https://github.com/mr-debayan/To-Do.git
cd To-Do
source .venv/bin/activate

pip install -r requirements-dev.txt   # first time only
python -m pytest -q
```

Expected output:

```
.................                                                        [100%]
17 passed in 0.13s
```

Useful variants:

```bash
python -m pytest -v                    # show each test name
python -m pytest tests/test_app.py::test_edit_changes_title -v
```

### What is covered

| Area | Tests |
| ---- | ----- |
| Rendering | empty state, GET-safe routes |
| Adding | normal title, blank input, whitespace trimming, 200-char limit |
| Safety | HTML/script input is escaped in the page |
| Completing | toggle on and off, unknown IDs, progress/count updates |
| Editing | title change, blank edit ignored |
| Deleting | single delete, "clear completed" keeps active tasks |
| Filters | active vs done, unknown filter fallback, filter kept after actions |

Each test uses its own temporary SQLite database, so your real `todo.db` is
never touched. No server needs to be running during the tests.

## 2. Manual checklist

Start the app and open <http://127.0.0.1:5000>:

```bash
source .venv/bin/activate
python app.py
```

Work through this list:

**Adding**
- [ ] Type a task and press **Add** — it appears at the top of the list.
- [ ] Press **Enter** in the input — same result.
- [ ] Click Add with an empty input — browser blocks it (form is `required`).
- [ ] Press **N** or **/** anywhere on the page — the input gets focus.
- [ ] Add a task with `<b>bold</b>` in the title — it shows the literal text,
      not bold (auto-escaping works).

**Completing**
- [ ] Click a task's circle — it fills in, the title gets struck through, and
      the counts/progress bar update.
- [ ] Click it again — the task goes back to active.
- [ ] Complete all tasks — progress reads 100%.

**Editing**
- [ ] Hover a task and click the pencil — an edit field opens with the title.
- [ ] Change the text, press **Save** — the new title is shown.
- [ ] Open an editor and press **Escape** or **Cancel** — it closes with no
      change.
- [ ] Save an empty title — the old title is kept.

**Deleting**
- [ ] Click the bin icon — a confirmation dialog appears.
- [ ] Press **Cancel** — the task stays.
- [ ] Click the bin again, then **OK** — the task is removed.

**Filters and counts**
- [ ] Add 3 tasks and complete 1.
- [ ] **All** shows 3, **Active** shows 2, **Done** shows 1.
- [ ] Complete a task while the Active filter is on — the page stays on Active
      and the task disappears from the list.

**Clearing**
- [ ] With completed tasks present, click **Clear completed tasks** — only the
      done tasks disappear.

**Persistence**
- [ ] Add a task, stop the server with **Ctrl+C**, start it again, reload —
      the task is still there (stored in `todo.db`).

**Look and feel**
- [ ] Narrow the browser window to phone width — layout stays usable and action
      buttons remain visible.
- [ ] Switch your OS to dark mode and reload — the app switches theme.
- [ ] Open the browser console (F12) — there should be no errors.

## 3. Quick smoke test from the terminal

If you only want to confirm the server responds:

```bash
# Show the page and HTTP status
curl -i http://127.0.0.1:5000/

# Add a task (302 redirect back to the list)
curl -i -X POST -d "title=Test from curl&filter=all" http://127.0.0.1:5000/add

# Confirm it was stored
curl -s http://127.0.0.1:5000/ | grep "Test from curl"
```

## Resetting the data

To start with an empty list, stop the server and delete the database:

```bash
rm todo.db
python app.py    # recreates an empty todo.db
```

## Troubleshooting

- **`ModuleNotFoundError: No module named 'flask'`** — the virtualenv is not
  active. Run `source .venv/bin/activate` first.
- **`Address already in use`** — another copy is running. Stop it with
  **Ctrl+C**, or start on another port:
  `flask --app app run --port 5001`.
- **Changes to CSS/JS not showing** — hard-reload the page
  (**Ctrl+Shift+R**).
- **Tests fail with a database error** — make sure you run pytest from the
  project folder, so `import app` resolves to this project.
