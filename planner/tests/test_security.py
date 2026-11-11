"""CS50 Week 8 – Caching, XSS and CSRF tests."""
from django.contrib.auth.models import User
from django.core.cache import cache  # noqa: F401
from django.test import Client
from django.urls import reverse

from planner import services
from planner.models import Task

from .helpers import TestCase, make_task, make_user

PASSWORD = "StrongPass123!"
XSS_PAYLOAD = "<script>alert('xss')</script>"


class DashboardCachingTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = make_user()

    def test_second_call_uses_cache_without_database_queries(self):
        make_task(self.user)
        services.get_dashboard_stats(self.user)              # fills the cache
        with self.assertNumQueries(0):                       # served from memory
            stats = services.get_dashboard_stats(self.user)
        self.assertEqual(stats["total"], 1)

    def test_first_call_hits_database(self):
        with self.assertNumQueries(4):  # total, completed, pending, overdue COUNTs
            services.get_dashboard_stats(self.user)

    def test_cache_is_cleared_when_task_created(self):
        self.assertEqual(services.get_dashboard_stats(self.user)["total"], 0)
        make_task(self.user)
        self.assertEqual(services.get_dashboard_stats(self.user)["total"], 1)

    def test_cache_is_cleared_when_task_edited(self):
        task = make_task(self.user)
        self.assertEqual(services.get_dashboard_stats(self.user)["completed"], 0)
        task.status = Task.Status.COMPLETED
        task.save()
        self.assertEqual(services.get_dashboard_stats(self.user)["completed"], 1)

    def test_cache_is_cleared_when_task_deleted(self):
        task = make_task(self.user)
        self.assertEqual(services.get_dashboard_stats(self.user)["total"], 1)
        task.delete()
        self.assertEqual(services.get_dashboard_stats(self.user)["total"], 0)

    def test_cache_is_per_user(self):
        other = make_user("bob")
        make_task(other)
        self.assertEqual(services.get_dashboard_stats(self.user)["total"], 0)
        self.assertEqual(services.get_dashboard_stats(other)["total"], 1)


class XssTests(TestCase):
    """Django auto-escapes template output, so script tags are shown as text."""

    def setUp(self):
        self.user = make_user()
        self.client.login(username="alice", password=PASSWORD)

    def test_malicious_title_and_description_are_escaped(self):
        make_task(self.user, title=XSS_PAYLOAD, description="<img src=x onerror=alert(1)>")
        html = self.client.get(reverse("task_list")).content.decode()
        self.assertNotIn(XSS_PAYLOAD, html)                       # raw script never appears
        self.assertIn("&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;", html)
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", html)

    def test_malicious_title_is_escaped_on_delete_page(self):
        task = make_task(self.user, title=XSS_PAYLOAD)
        html = self.client.get(reverse("task_delete", args=[task.pk])).content.decode()
        self.assertNotIn(XSS_PAYLOAD, html)

    def test_malicious_title_submitted_through_form_is_stored_and_escaped(self):
        self.client.post(reverse("task_add"), {
            "title": XSS_PAYLOAD, "description": "", "due_date": "2030-01-01",
            "priority": "low", "status": "pending"})
        html = self.client.get(reverse("task_list")).content.decode()
        self.assertNotIn(XSS_PAYLOAD, html)
        self.assertIn("&lt;script&gt;", html)

    def test_templates_never_mark_user_content_safe(self):
        from pathlib import Path
        from django.conf import settings
        for path in Path(settings.BASE_DIR, "templates").rglob("*.html"):
            text = path.read_text()
            self.assertNotIn("|safe", text, path.name)
            self.assertNotIn("autoescape off", text, path.name)


class CsrfTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_post_without_csrf_token_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        client.login(username="alice", password=PASSWORD)
        response = client.post(reverse("task_add"), {
            "title": "Forged", "due_date": "2030-01-01", "priority": "low", "status": "pending"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Task.objects.count(), 0)

    def test_login_post_without_csrf_token_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("login"), {"username": "alice", "password": PASSWORD})
        self.assertEqual(response.status_code, 403)

    def test_delete_without_csrf_token_is_rejected(self):
        task = make_task(self.user)
        client = Client(enforce_csrf_checks=True)
        client.login(username="alice", password=PASSWORD)
        self.assertEqual(client.post(reverse("task_delete", args=[task.pk])).status_code, 403)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_post_with_valid_csrf_token_works(self):
        client = Client(enforce_csrf_checks=True)
        client.login(username="alice", password=PASSWORD)
        page = client.get(reverse("task_add"))                    # form contains the token
        token = page.cookies["csrftoken"].value
        response = client.post(reverse("task_add"), {
            "title": "Legit", "due_date": "2030-01-01", "priority": "low",
            "status": "pending", "csrfmiddlewaretoken": token})
        self.assertRedirects(response, reverse("task_list"))
        self.assertTrue(Task.objects.filter(title="Legit").exists())

    def test_forms_contain_csrf_token(self):
        self.client.login(username="alice", password=PASSWORD)
        for name in ("task_add",):
            self.assertContains(self.client.get(reverse(name)), "csrfmiddlewaretoken")
        self.assertContains(self.client.get(reverse("login")), "csrfmiddlewaretoken")

    def test_csrf_middleware_is_enabled(self):
        from django.conf import settings
        self.assertIn("django.middleware.csrf.CsrfViewMiddleware", settings.MIDDLEWARE)
