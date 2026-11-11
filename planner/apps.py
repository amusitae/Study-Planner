from django.apps import AppConfig


class PlannerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "planner"

    def ready(self):
        # Connects the signals that clear the dashboard cache (Week 8: caching).
        from . import signals  # noqa: F401
