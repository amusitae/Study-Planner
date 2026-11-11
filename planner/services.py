"""
Business logic for task statistics, kept separate from views so it is easy to
unit-test (CS50 Week 7: unit testing / TDD) and to cache (Week 8: caching).
"""
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .models import Task


def completion_percentage(total, completed):
    """Whole-number percentage of completed tasks. 0 when there are no tasks."""
    if total <= 0:
        return 0
    return round(completed * 100 / total)


def count_completed(tasks):
    return tasks.filter(status=Task.Status.COMPLETED).count()


def count_pending(tasks):
    return tasks.filter(status=Task.Status.PENDING).count()


def overdue_tasks(tasks, today=None):
    """Pending tasks whose due date is before today. Completed tasks are never overdue."""
    today = today or timezone.localdate()
    return tasks.filter(status=Task.Status.PENDING, due_date__lt=today)


def calculate_dashboard_stats(user):
    tasks = Task.objects.filter(owner=user)
    total = tasks.count()
    completed = count_completed(tasks)
    return {
        "total": total,
        "completed": completed,
        "pending": count_pending(tasks),
        "overdue": overdue_tasks(tasks).count(),
        "percentage": completion_percentage(total, completed),
    }


def dashboard_cache_key(user_id):
    return f"dashboard_stats:{user_id}"


def get_dashboard_stats(user):
    """
    Return the dashboard numbers, using the cache when possible.

    First call  -> several COUNT queries, result stored for DASHBOARD_CACHE_TIMEOUT.
    Next calls  -> served from memory, 0 database queries.
    Signals (planner/signals.py) delete the cached value whenever a task changes.
    """
    key = dashboard_cache_key(user.pk)
    stats = cache.get(key)
    if stats is None:
        stats = calculate_dashboard_stats(user)
        cache.set(key, stats, settings.DASHBOARD_CACHE_TIMEOUT)
    return stats


def invalidate_dashboard_stats(user_id):
    cache.delete(dashboard_cache_key(user_id))
