"""
CS50 Week 7 – Unit testing and Test-Driven Development (TDD).

TDD cycle used for these functions:
  1. RED    – write the test first; run it; it fails (function missing / wrong).
  2. GREEN  – write the smallest code in planner/services.py that makes it pass.
  3. REFACTOR – clean the code and re-run the tests to make sure they still pass.
"""
import unittest



from planner import services
from planner.models import Task

from .helpers import TestCase, make_task, make_user


class CompletionPercentageUnitTests(unittest.TestCase):
    """Pure-Python unit tests (python's unittest, no database needed)."""

    def test_zero_tasks_gives_zero_percent(self):
        self.assertEqual(services.completion_percentage(0, 0), 0)

    def test_half_completed(self):
        self.assertEqual(services.completion_percentage(4, 2), 50)

    def test_all_completed(self):
        self.assertEqual(services.completion_percentage(5, 5), 100)

    def test_rounding(self):
        self.assertEqual(services.completion_percentage(3, 1), 33)


class TaskCountingTests(TestCase):
    def setUp(self):
        self.user = make_user()
        make_task(self.user, "a", status=Task.Status.COMPLETED)
        make_task(self.user, "b", status=Task.Status.COMPLETED)
        make_task(self.user, "c", status=Task.Status.PENDING)
        self.tasks = Task.objects.filter(owner=self.user)

    def test_count_completed(self):
        self.assertEqual(services.count_completed(self.tasks), 2)

    def test_count_pending(self):
        self.assertEqual(services.count_pending(self.tasks), 1)

    def test_counts_are_empty_for_new_user(self):
        other = make_user("bob")
        tasks = Task.objects.filter(owner=other)
        self.assertEqual(services.count_completed(tasks), 0)
        self.assertEqual(services.count_pending(tasks), 0)


class OverdueTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_past_pending_task_is_overdue(self):
        late = make_task(self.user, "late", days=-2)
        result = services.overdue_tasks(Task.objects.filter(owner=self.user))
        self.assertEqual(list(result), [late])
        self.assertTrue(late.is_overdue)

    def test_future_task_is_not_overdue(self):
        make_task(self.user, "future", days=2)
        self.assertEqual(services.overdue_tasks(Task.objects.filter(owner=self.user)).count(), 0)

    def test_due_today_is_not_overdue(self):
        make_task(self.user, "today", days=0)
        self.assertEqual(services.overdue_tasks(Task.objects.filter(owner=self.user)).count(), 0)

    def test_completed_past_task_is_not_overdue(self):
        done = make_task(self.user, "done", days=-5, status=Task.Status.COMPLETED)
        self.assertEqual(services.overdue_tasks(Task.objects.filter(owner=self.user)).count(), 0)
        self.assertFalse(done.is_overdue)


class DashboardStatsTests(TestCase):
    def test_stats_dictionary(self):
        user = make_user()
        make_task(user, "1", status=Task.Status.COMPLETED)
        make_task(user, "2", days=-1)
        make_task(user, "3", days=4)
        make_task(user, "4", days=4, status=Task.Status.COMPLETED)
        stats = services.calculate_dashboard_stats(user)
        self.assertEqual(stats, {"total": 4, "completed": 2, "pending": 2,
                                 "overdue": 1, "percentage": 50})
