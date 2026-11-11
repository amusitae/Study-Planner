# Architecture & CS50 Concept Mapping

## Design
Django MVT: **Model** (`planner/models.py`) → **View** (`planner/views.py`) → **Template** (`templates/`).
Statistics logic lives in `planner/services.py` so it can be unit-tested and cached independently of the web layer.

## Database (SQLite)

**auth_user** (built-in Django) 1 ──── * **Task**

| Task field   | Type                              | Notes                          |
|--------------|-----------------------------------|--------------------------------|
| id           | BigAutoField (PK)                 |                                |
| owner        | ForeignKey → User (CASCADE)       | enforces per-user data         |
| title        | CharField(200)                    | required                       |
| description  | TextField                         | optional                       |
| due_date     | DateField                         | required                       |
| priority     | low / medium / high               | default medium                 |
| status       | pending / completed               | default pending                |
| created_at   | DateTimeField (auto)              |                                |

"Overdue" is not stored; it is computed: `status == pending AND due_date < today`.

## Pages
Login · Register · Dashboard (`/`) · All Tasks (`/tasks/`, with search + filters) · Add Task · Edit Task · Delete confirmation.

## Security design
- All task views require login and query only `Task.objects.filter(owner=request.user)`; another user's id returns **404**.
- Passwords hashed by Django (PBKDF2); validators reject weak passwords.
- Inputs validated by Django forms; filter values validated by `TaskFilterForm`.
- State-changing actions (logout, complete, delete) are POST-only with CSRF tokens.

## CS50 concept → project mapping

Status: **Implemented** = working code that is tested/run. **Documented** = explanation or demo only.

| CS50 topic | Status | Where |
|---|---|---|
| Week 7 – Test-Driven Development | Implemented (process shown in docs) | `planner/tests/test_services.py`, `planner/services.py`, `docs/WEEK7.md` |
| Week 7 – Unit testing | Implemented | `planner/tests/test_services.py` (`unittest` + Django `TestCase`) |
| Week 7 – Django testing (client, auth, CRUD) | Implemented | `planner/tests/test_views.py`, `test_security.py` |
| Week 7 – Selenium | Implemented (needs Chrome; skipped otherwise) | `planner/tests/test_selenium.py` |
| Week 7 – CI/CD, GitHub Actions | Implemented (runs after you push to GitHub) | `.github/workflows/tests.yml` |
| Week 7 – Docker | Files implemented; build/run **must be done and checked by you** | `Dockerfile`, `.dockerignore`, `requirements.txt` |
| Week 8 – Caching | Implemented + tested | `planner/services.py`, `planner/signals.py`, `config/settings.py` (`CACHES`), `test_security.py` |
| Week 8 – XSS | Implemented (Django auto-escaping) + tested | `templates/`, `XssTests` |
| Week 8 – CSRF | Implemented (middleware + tokens) + tested | `config/settings.py`, templates, `CsrfTests` |
| Week 8 – HTTPS | Configuration provided; **documented only** (no certificate used locally) | `config/settings.py` (`DJANGO_HTTPS`), `docs/WEEK8.md` |
| Week 8 – Public-key cryptography | Educational demo + docs (not used by the app) | `scripts/public_key_demo.py`, `docs/WEEK8.md` |
| Week 8 – Load balancing | Demo config provided (needs Docker to run); explained | `docker-compose.yml`, `nginx/nginx.conf`, `docs/WEEK8.md` |
| Week 8 – Autoscaling | **Documented only** | `docs/WEEK8.md` |
| Week 8 – Database replication | **Documented only**; a *backup* script is included and is not replication | `docs/WEEK8.md`, `scripts/backup_db.py` |

## Why a few extra packages?
`selenium` (required by the brief), plus `gunicorn` (a real web server – Django's `runserver` is for development only)
and `whitenoise` (lets gunicorn serve the CSS inside Docker). Both are only needed for the Docker/production path.
