# Presentation script (≈ 8 minutes) and evidence checklist

1. **Intro (30 s)** – "Study Planner helps students manage tasks and deadlines. Built with Django, SQLite, Bootstrap."
2. **Live demo (2 min)** – register → add 3 tasks (one overdue, one high priority) → dashboard numbers → filter/search → mark complete → dashboard updates.
3. **Privacy (30 s)** – second account sees none of the first account's tasks; opening their URL gives 404.
4. **Week 7 (2 min)** – show `test_services.py` (TDD), run `python manage.py test` (green), show Selenium test, GitHub Actions green run, Docker running.
5. **Week 8 (2 min)** – caching (0 queries on second dashboard load), XSS demo (script shown as text), CSRF test (403), explain HTTPS / public keys / load balancing / autoscaling / replication, and say clearly which are documented only.
6. **Conclusion (30 s)** – what was learned, limitations (SQLite, per-process cache, HTTPS needs real deployment).

## Screenshots to collect
- [ ] Login, Register, Dashboard, All Tasks (with filters), Add/Edit Task
- [ ] Terminal: `python manage.py test` result
- [ ] Failing test (RED) then passing test (GREEN) for the TDD example
- [ ] Selenium test passing (or the browser window while it runs)
- [ ] GitHub Actions green run
- [ ] `docker build` + `docker run` + browser at localhost:8000
- [ ] XSS payload displayed as text
- [ ] CSRF test result (403 case passing)
- [ ] `public_key_demo.py` output and `backup_db.py` output
