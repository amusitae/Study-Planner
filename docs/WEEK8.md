# CS50 Week 8 – Scalability and Security

Course page: https://cs50.harvard.edu/web/weeks/8/ (topics: load balancing, autoscaling, database replication, caching, HTTPS, public-key cryptography, XSS, CSRF)

Legend: ✅ implemented and tested in code · 📘 explained / demo only

## Caching ✅
`get_dashboard_stats()` (`planner/services.py`) stores the five dashboard numbers in Django's cache under `dashboard_stats:<user_id>`
for 5 minutes (`DASHBOARD_CACHE_TIMEOUT`). First visit: 4 `COUNT` queries. Next visits: **0 queries** (`test_second_call_uses_cache_without_database_queries`).
`planner/signals.py` deletes the entry on every task create / edit / delete / status change, so numbers are never stale
(`test_cache_is_cleared_when_task_*`). Note: `LocMemCache` is per process; several servers would need a shared cache such as Redis.

## XSS ✅
Django templates escape `<`, `>`, `&`, quotes automatically. Nothing in `templates/` uses `|safe` or `autoescape off` (a test checks this).
**Safe demo:** log in → Add Task with title `<script>alert('XSS')</script>` → open *All Tasks*. The text appears literally and no alert pops up.
In "view source" you will see `&lt;script&gt;…`. Automated proof: `XssTests`.

## CSRF ✅
`CsrfViewMiddleware` is enabled; every POST form contains `{% csrf_token %}` (including Logout). `CsrfTests` use a client with
`enforce_csrf_checks=True`: a POST without token → **403** and nothing is saved; with a valid token → works.

## HTTPS 📘 (configuration provided)
HTTPS = HTTP inside TLS: traffic is encrypted (nobody on the network can read passwords/session cookies), tamper-proof, and the server's
certificate proves you reached the real site. Local `http://127.0.0.1:8000` is **not** HTTPS.
Deployment steps:
1. Get a domain and a certificate (free: Let's Encrypt / Certbot, or your host's automatic TLS).
2. Put a web server (nginx/Caddy) or hosting platform in front of the app to terminate TLS and forward `X-Forwarded-Proto: https`.
3. Set `DJANGO_HTTPS=1`, a real `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, and `DJANGO_ALLOWED_HOSTS=yourdomain.com`.
   This turns on (see `config/settings.py`): HTTPS redirect, secure session/CSRF cookies and HSTS.

## Public-key cryptography 📘
Two mathematically linked keys: the **public key** (shared) locks data / verifies signatures; the **private key** (secret) unlocks / signs.
In TLS the certificate carries the server's public key; the browser and server use it to agree on a fresh shared session key, then
use fast symmetric encryption for the actual traffic. Run `python scripts/public_key_demo.py` for a toy RSA walk-through
(tiny numbers, **not secure, not used by the app**). Passwords are protected with Django's hashing, not custom cryptography.

## Load balancing 📘 + demo config
A load balancer receives all requests and spreads them over several identical app servers, so no single server is overloaded and one can fail safely.
`docker compose up --build` starts `app1`, `app2` and an nginx round-robin balancer on http://localhost:8080 (`nginx/nginx.conf`).
It is a classroom demo (shared SQLite file, per-server cache) – not production infrastructure. Requires Docker; not run in the generation environment.

## Autoscaling 📘
```
 users → Load balancer → [App server 1] [App server 2] … [App server N] → shared database + shared cache
                               ▲
              monitor CPU / requests per second
              CPU > 70 %  → start more servers (scale out)
              CPU < 30 %  → stop extra servers (scale in)
```
Cloud platforms (AWS Auto Scaling, Kubernetes HPA, Azure scale sets, Cloud Run) do this automatically within a minimum/maximum number of instances.
For this app to scale out it needs a shared database (e.g. PostgreSQL) and shared cache (Redis) instead of per-server SQLite/LocMem.

## Database replication 📘 (and backup ✅)
**Replication** keeps one or more *replica* databases continuously synchronised with a *primary*: replicas serve read queries (more capacity)
and can take over if the primary fails (availability). **Backup** is a copy at one moment, used for recovery, and is *not* replication.
`python scripts/backup_db.py` makes a timestamped backup in `backups/` with SQLite's backup API. SQLite has no built-in live replication;
that needs a server database such as PostgreSQL.
