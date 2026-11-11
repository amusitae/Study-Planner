# CS50 Week 7 – Testing, CI/CD

Course page: https://cs50.harvard.edu/web/weeks/7/ (topics: TDD, unit testing, Django testing, Selenium, CI/CD, GitHub Actions, Docker)

## 1. Test-Driven Development (TDD)
Example: `overdue_tasks()` in `planner/services.py`.

1. **Write the test first** (`OverdueTests` in `planner/tests/test_services.py`):
   a past pending task must be overdue; a future, due-today or completed task must not be.
2. **Run it – it must fail (RED):**
   `python manage.py test planner.tests.test_services.OverdueTests`
   (before the function exists you get an `AttributeError`).
3. **Write the smallest code that passes (GREEN):**
   ```python
   def overdue_tasks(tasks, today=None):
       today = today or timezone.localdate()
       return tasks.filter(status=Task.Status.PENDING, due_date__lt=today)
   ```
4. **Run again – all pass.** Then refactor if needed and re-run.

*Try it yourself for evidence:* temporarily change `due_date__lt` to `due_date__lte`, run the tests, watch
`test_due_today_is_not_overdue` fail, then change it back. That shows the tests really protect behaviour.

## 2. Unit tests (`planner/tests/test_services.py`)
| Required function | Tests |
|---|---|
| Count completed | `TaskCountingTests.test_count_completed` |
| Count pending | `TaskCountingTests.test_count_pending` |
| Completion percentage | `CompletionPercentageUnitTests` (plain `unittest.TestCase`, no DB) |
| Overdue tasks | `OverdueTests` |

## 3. Django tests (`planner/tests/test_views.py`)
Registration (success, mismatch, duplicate, weak password) · login/logout (success + failure) · add/edit/delete/complete
(success + invalid input) · dashboard access and numbers · anonymous users redirected to login ·
**data isolation** (another user's task cannot be listed, opened, edited, deleted or completed) · search and filters.

## 4. Selenium (`planner/tests/test_selenium.py`)
Headless Chrome opens the login page → enters credentials → logs in → opens *Add Task* → saves a task → checks the task text appears.

Install and run:
```bash
pip install selenium            # already in requirements.txt
# install Google Chrome from https://www.google.com/chrome/
python manage.py test planner.tests.test_selenium -v 2
```
To *watch* the browser, delete the `--headless=new` line in the test file temporarily.
Without Chrome the test shows as `skipped`.

## 5. CI/CD – GitHub Actions (`.github/workflows/tests.yml`)
On every **push** and **pull request**: checkout → set up Python 3.12 → `pip install -r requirements.txt` → `manage.py check` → `manage.py test`.
A green ✔ or red ✘ appears on the commit/PR. Evidence: screenshot of the Actions tab after you push.

## 6. Docker
Files: `Dockerfile`, `.dockerignore`, `requirements.txt`.
```bash
docker build -t study-planner .
docker run --rm -p 8000:8000 -v study_planner_data:/data study-planner
```
Check http://localhost:8000/ and take a screenshot plus `docker ps` output as evidence.
Run tests inside the image: `docker run --rm study-planner python manage.py test`
(Selenium will be skipped there because the slim image has no Chrome).
