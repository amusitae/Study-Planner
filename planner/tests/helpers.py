from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from planner.models import Task


def make_user(username="alice", password="StrongPass123!"):
    return User.objects.create_user(username=username, password=password)


def make_task(owner, title="Read chapter 1", days=3, status=Task.Status.PENDING,
              priority=Task.Priority.MEDIUM, description=""):
    """days > 0 = due in the future, days < 0 = already past."""
    return Task.objects.create(
        owner=owner, title=title, description=description,
        due_date=timezone.localdate() + timedelta(days=days),
        status=status, priority=priority,
    )


from django.core.cache import cache  # noqa: E402
from django.test import TestCase as DjangoTestCase  # noqa: E402


class TestCase(DjangoTestCase):
    """Django TestCase that also empties the cache before every test.

    The database is rolled back after each test but the cache is not, so
    without this, cached dashboard numbers could leak from one test to another.
    """

    def _pre_setup(self):
        super()._pre_setup()
        cache.clear()
