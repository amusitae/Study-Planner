"""CS50 Week 7 – Django tests: authentication, CRUD, dashboard, permissions, isolation."""
from django.contrib.auth.models import User

from django.urls import reverse

from planner.models import Task

from .helpers import TestCase, make_task, make_user

PASSWORD = "StrongPass123!"


class RegistrationTests(TestCase):
    def test_register_success_creates_user_and_logs_in(self):
        response = self.client.post(reverse("register"), {
            "username": "newstudent", "password1": PASSWORD, "password2": PASSWORD})
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.get(username="newstudent")
        self.assertNotEqual(user.password, PASSWORD)          # stored hashed
        self.assertTrue(user.password.startswith("pbkdf2_"))  # Django's hasher
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_register_password_mismatch_fails(self):
        response = self.client.post(reverse("register"), {
            "username": "x", "password1": PASSWORD, "password2": "different"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="x").exists())

    def test_register_duplicate_username_fails(self):
        make_user("taken")
        response = self.client.post(reverse("register"), {
            "username": "taken", "password1": PASSWORD, "password2": PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="taken").count(), 1)

    def test_register_weak_password_fails(self):
        response = self.client.post(reverse("register"), {
            "username": "weak", "password1": "12345678", "password2": "12345678"})
        self.assertFalse(User.objects.filter(username="weak").exists())
        self.assertEqual(response.status_code, 200)


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_login_success(self):
        response = self.client.post(reverse("login"), {"username": "alice", "password": PASSWORD})
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_wrong_password_fails(self):
        response = self.client.post(reverse("login"), {"username": "alice", "password": "nope"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout(self):
        self.client.login(username="alice", password=PASSWORD)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class AuthenticationRequiredTests(TestCase):
    def test_protected_pages_redirect_anonymous_users_to_login(self):
        task = make_task(make_user())
        urls = [reverse("dashboard"), reverse("task_list"), reverse("task_add"),
                reverse("task_edit", args=[task.pk]), reverse("task_delete", args=[task.pk])]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response["Location"].startswith(reverse("login")))

    def test_anonymous_cannot_complete_task(self):
        task = make_task(make_user())
        self.client.post(reverse("task_complete", args=[task.pk]))
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.PENDING)


class TaskCrudTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.login(username="alice", password=PASSWORD)

    def test_add_task_success(self):
        response = self.client.post(reverse("task_add"), {
            "title": "Study Django", "description": "Chapter 3", "due_date": "2030-01-01",
            "priority": "high", "status": "pending"})
        self.assertRedirects(response, reverse("task_list"))
        task = Task.objects.get(title="Study Django")
        self.assertEqual(task.owner, self.user)
        self.assertEqual(task.priority, "high")

    def test_add_task_missing_title_fails(self):
        response = self.client.post(reverse("task_add"), {
            "title": "   ", "due_date": "2030-01-01", "priority": "low", "status": "pending"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 0)

    def test_add_task_invalid_date_fails(self):
        response = self.client.post(reverse("task_add"), {
            "title": "x", "due_date": "not-a-date", "priority": "low", "status": "pending"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 0)

    def test_add_task_invalid_priority_fails(self):
        response = self.client.post(reverse("task_add"), {
            "title": "x", "due_date": "2030-01-01", "priority": "urgent", "status": "pending"})
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_task_list_shows_own_tasks(self):
        make_task(self.user, "Visible task")
        self.assertContains(self.client.get(reverse("task_list")), "Visible task")

    def test_edit_task_success(self):
        task = make_task(self.user, "Old title")
        response = self.client.post(reverse("task_edit", args=[task.pk]), {
            "title": "New title", "description": "", "due_date": "2030-05-05",
            "priority": "low", "status": "pending"})
        self.assertRedirects(response, reverse("task_list"))
        task.refresh_from_db()
        self.assertEqual((task.title, task.priority), ("New title", "low"))

    def test_edit_task_invalid_data_keeps_old_value(self):
        task = make_task(self.user, "Keep me")
        self.client.post(reverse("task_edit", args=[task.pk]), {
            "title": "", "due_date": "2030-05-05", "priority": "low", "status": "pending"})
        task.refresh_from_db()
        self.assertEqual(task.title, "Keep me")

    def test_delete_task_success(self):
        task = make_task(self.user)
        response = self.client.post(reverse("task_delete", args=[task.pk]))
        self.assertRedirects(response, reverse("task_list"))
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_mark_task_completed(self):
        task = make_task(self.user)
        self.client.post(reverse("task_complete", args=[task.pk]))
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.COMPLETED)

    def test_complete_requires_post(self):
        task = make_task(self.user)
        response = self.client.get(reverse("task_complete", args=[task.pk]))
        self.assertEqual(response.status_code, 405)


class DashboardTests(TestCase):
    def test_dashboard_access_and_numbers(self):
        user = make_user()
        make_task(user, "a", status=Task.Status.COMPLETED)
        make_task(user, "b", days=-1)
        self.client.login(username="alice", password=PASSWORD)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        stats = response.context["stats"]
        self.assertEqual((stats["total"], stats["completed"], stats["pending"],
                          stats["overdue"], stats["percentage"]), (2, 1, 1, 1, 50))


class DataIsolationTests(TestCase):
    """Users must never see or change another user's tasks."""

    def setUp(self):
        self.alice = make_user("alice")
        self.bob = make_user("bob")
        self.bobs_task = make_task(self.bob, "Bob secret task")
        self.client.login(username="alice", password=PASSWORD)

    def test_list_hides_other_users_tasks(self):
        self.assertNotContains(self.client.get(reverse("task_list")), "Bob secret task")

    def test_dashboard_counts_only_own_tasks(self):
        self.assertEqual(self.client.get(reverse("dashboard")).context["stats"]["total"], 0)

    def test_cannot_open_edit_page_of_other_user(self):
        self.assertEqual(self.client.get(reverse("task_edit", args=[self.bobs_task.pk])).status_code, 404)

    def test_cannot_edit_other_users_task(self):
        self.client.post(reverse("task_edit", args=[self.bobs_task.pk]), {
            "title": "Hacked", "due_date": "2030-01-01", "priority": "low", "status": "pending"})
        self.bobs_task.refresh_from_db()
        self.assertEqual(self.bobs_task.title, "Bob secret task")

    def test_cannot_delete_other_users_task(self):
        response = self.client.post(reverse("task_delete", args=[self.bobs_task.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(pk=self.bobs_task.pk).exists())

    def test_cannot_complete_other_users_task(self):
        response = self.client.post(reverse("task_complete", args=[self.bobs_task.pk]))
        self.assertEqual(response.status_code, 404)
        self.bobs_task.refresh_from_db()
        self.assertEqual(self.bobs_task.status, Task.Status.PENDING)


class SearchAndFilterTests(TestCase):
    def setUp(self):
        user = make_user()
        make_task(user, "Math homework", priority="high")
        make_task(user, "History essay", priority="low", status=Task.Status.COMPLETED)
        make_task(user, "Math quiz prep", priority="low", days=-3)
        self.client.login(username="alice", password=PASSWORD)

    def titles(self, **params):
        response = self.client.get(reverse("task_list"), params)
        return sorted(t.title for t in response.context["tasks"])

    def test_search_by_title(self):
        self.assertEqual(self.titles(q="math"), ["Math homework", "Math quiz prep"])

    def test_filter_by_status(self):
        self.assertEqual(self.titles(status="completed"), ["History essay"])

    def test_filter_by_priority(self):
        self.assertEqual(self.titles(priority="high"), ["Math homework"])

    def test_filter_overdue(self):
        self.assertEqual(self.titles(overdue="on"), ["Math quiz prep"])

    def test_invalid_filter_value_is_ignored(self):
        self.assertEqual(len(self.titles(status="hacked")), 3)
